# -*- coding: utf-8 -*-

import telebot
import logging

from keyboard import create_keyboard
from access import check_access
import question as qa
import users
import config
import distance

logging.basicConfig(filename=config.BOT_CONFIG['LOGFILE'], level=logging.DEBUG)
bot = telebot.TeleBot(config.BOT_CONFIG['TOKEN'])


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    When a user sends the /start command a bot saves him to a full db of users,
    then sends a greeting with buttons to get a question or get nothing :)
    """
    saved_user = users.save_user(message)
    warning = ''
    if not saved_user['username']:
        warning = 'Настоятельно рекомендую завести юзернейм. Пожалуйста.'

    bot.send_message(message.chat.id, f"Даров, {saved_user['first_name']}. "+warning)
    logging.info(f'Пользователь {message.chat.id} - {message.chat.first_name} присоединился.')

    button_names = ['Получить вопрос', '???']
    callbacks = ['get_question', 'do_nothing']
    bot.send_message(message.chat.id, "За вопросами пришел?", reply_markup=create_keyboard(button_names, callbacks))


@bot.message_handler(commands=['get_question'])
def get_question(message):
    users.save_user(message)  # TODO: убрать по наполнению базы. Костыль для лохов.
    current_question = qa.CurrentQuestion()

    if current_question.question:
        bot.send_message(message.chat.id,
                         f'<b>Вопрос:</b> {current_question.question}',
                         parse_mode='HTML')
        if message.chat.id != config.BOT_CONFIG['ADMIN_ID']:  # admin can't be answering since he's omniscient
            users.add_answering_person(message)
    else:
        bot.send_message(message.chat.id, 'Скажи Ане шо вопросы кончились плз.')
        button_names = ['Сказать', 'Не сказать']
        callbacks = ['kick_admin', 'do_nothing']
        bot.send_message(message.chat.id, "Есть два стула.", reply_markup=create_keyboard(button_names, callbacks))


@bot.message_handler(commands=['reset_users_dbs'])
@check_access
def reset_dbs(message):
    users.reset_dbs()
    bot.send_message(message.chat.id, 'Базы рип.')


@bot.message_handler(commands=['print_all_questions'])
@check_access
def print_all_questions(message):
    questions = qa.get_all_questions()
    for question in questions:
        comment = question[3]
        bot.send_message(message.chat.id, f'{question[0]}. {question[1]} \n {question[2]} \n {comment}')


@bot.message_handler(commands=['close_current_question'])
@check_access
def close_current_question(message):
    answered_list = [str(i) for i in users.get_answered_persons_ids()]
    answered = ', '.join(answered_list)

    if len(answered) == 0:
        answered = "¯\_(ツ)_/¯"
    current_question = qa.CurrentQuestion()
    answer = current_question.answer
    comment = current_question.comment or ''

    question_user_list = users.get_answered_persons_ids() + users.get_answering_persons_ids() + [config.BOT_CONFIG['ADMIN_ID']]
    qa.close_current_question()
    users.reset_dbs()

    for uid in question_user_list:
        try:
            bot.send_message(uid, f'Ответили: {answered}')
            bot.send_message(uid, f'Ответ: {answer} \n' + comment)
        except Exception as e:
            logging.info(f'Oops. {uid}, {e}.')

    button_names = ['Получить вопрос', 'Послать ответившим <3']
    callbacks = ['get_question', 'send_love_to_winners']

    for uid in users.get_all_users_ids():
        try:
            bot.send_message(id, "Новый вопрос подъехал.", reply_markup=create_keyboard(button_names, callbacks))
        except Exception as e:
            logging.info(f'Oops. {uid}, {e}.')


@bot.message_handler(commands=['check_archive'])
@check_access
def check_archive(message):
    data = qa.check_archive()
    for item in data:
        logging.info(f'archive: { item }')


@bot.message_handler(commands=['delete_all_questions'])
@check_access
def delete_questions(message):
    qa.drop_the_db()
    bot.send_message(message.chat.id, 'Вопросы рип.')


@bot.message_handler(commands=['delete_question'])
@check_access
def delete_question(message):
    qid_list = message.text.split()
    qid_list.pop(0)
    for qid in qid_list:
        qa.delete_one_question(qid)
    bot.send_message(message.chat.id, 'Done.')


@bot.message_handler(commands=['notify_members'])
@check_access
def notify_all(message):
    text = message.text.replace('/notify_members ', '')
    user_list = users.get_all_users_ids()
    for user in user_list:
        try:
            bot.send_message(user['uid'], text)
            logging.info(f'{text} was sent to {user["uid"]}')
        except Exception as e:
            logging.info(f'Oops. {user["uid"]}, {user["username"]}, {e}.')


@bot.message_handler(commands=['change_question'])
@check_access
def change_question(message):
    """
    takes input in a following format:
    /change_question <_id> <type> text
    E.g.:
    /change_question 5c6ac5fe450b92ac3bebb308 answer Random text to be inserted instead of previous one.
    """
    text = message.text.replace('/change_question ', '')

    # taking _id and removing _id from the string
    qid = text[:text.index(' ')]
    text = text.replace(qid, '').strip()

    # taking property and removing it from the string
    question_property = text[:text.index(' ')]
    text = text.replace(question_property, '').strip()

    qa.change_question_by_number(qid, question_property, text)
    logging.info(f'{question_property} is changed to {text}')


@bot.message_handler(func=lambda m: True)
def handle_message(message):

    # if a user is in a state of answering
    if message.chat.id in users.get_answering_persons_ids():
        right_answer = qa.CurrentQuestion().answer
        difference = distance.calc_distance(message.text.lower(), right_answer.lower())
        logging.info(f'{ message.chat.username } answers {message.text} while answer is: {right_answer}. '
                     f'Difference: { difference }')
        if distance.calc_distance(message.text.lower(), 'помедор') <= 3:
            bot.send_message(message.chat.id, '30 очков Гриффиндору.')

        if difference <= 3:  # correct answer
            users.move_to_answered(message.chat)
            bot.send_message(message.chat.id, 'Засчитано! Надо бы усложнить вопросы.')
            bot.send_message(config.BOT_CONFIG['ADMIN_ID'], f'{ message.chat.username } ответил.')
        else:  # wrong answer
            bot.send_message(message.chat.id, f'Нет. Разница: { difference }')

    elif message.chat.id in users.get_answered_persons_ids():
        bot.send_message(message.chat.id, 'Расслабься, засчитано. Выпей чаю.')

    # handling adding of questions
    elif message.chat.id == config.BOT_CONFIG['ADMIN_ID']:
        try:
            new_question = qa.Question(message.text)
            new_question.add_to_db()
            bot.send_message(message.chat.id, 'Вопрос успешно добавлен.')
        except ValueError:
            bot.send_message(message.chat.id, 'Это не вопрос :(')

    elif message.chat.id:
        logging.info(f'Caught {message.chat.id, message.chat.username} with { message.text }')


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'get_question':
        get_question(call.message)

    if call.data == 'send_love':
        bot.send_message(config.BOT_CONFIG['ADMIN_ID'], '<3')
        logging.info(f'Love was sent by { call.message.chat.username }')

    if call.data == 'send_love_to_winners':
        uids = qa.get_last_winners()
        for uid in uids:
            bot.send_message(uid, f'<3 from { call.message.chat.username }')

        button_names = ['Получить вопрос']
        callbacks = ['get_question']

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Послано.', reply_markup=create_keyboard(button_names, callbacks))

        logging.info(f'Love to winners was sent by { call.message.chat.username }')

    if call.data == 'do_nothing':
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="doing nothing")

    if call.data == 'kick_admin':
        bot.send_message(config.BOT_CONFIG['ADMIN_ID'], 'Вопросы рип, примите меры.')


bot.polling()
