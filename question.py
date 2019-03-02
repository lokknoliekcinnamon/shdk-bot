import logging
from db import db
from bson.objectid import ObjectId
import re
from pymongo import ReturnDocument


class Question:
    """
    This class represents questions created by processing raw text sent by admin of a channel.
    """
    def __init__(self, input_line):
        self.raw_input = input_line

        beginning_of_question = input_line.index(':')+1
        end_of_question = input_line.index('Ответ:') - 4
        self.question = input_line[beginning_of_question:end_of_question].strip()

        try:
            text_between_brackets = re.findall('\[(.*?)\]', self.question)
            for i in text_between_brackets:
                logging.info(i)
                i = '[' + i + ']'
                self.question = self.question.replace(i, '')
                logging.info(f'Removed {i} from a question.')
        except TypeError:
            logging.info('No brackets found.')

        beginning_of_answer = input_line.index('Ответ:') + 6
        end_of_answer = beginning_of_answer + input_line[beginning_of_answer:].index('.')
        self.answer = input_line[beginning_of_answer:end_of_answer].strip()

        try:
            beginning_of_comment = input_line.index('Комментарий:') + 12
            end_of_comment = input_line.index('Источник')
            self.comment = input_line[beginning_of_comment:end_of_comment].strip()
        except ValueError:
            self.comment = None
            logging.info('A comment is missing.')

        logging.info(f'Question was created.')

    def get_raw_input(self):
        return self.raw_input

    def get_question(self):
        return self.question

    def get_answer(self):
        return self.answer

    def get_comment(self):
        return self.comment

    def add_to_db(self):
        questions = db.questions
        question_data = {
            'question': self.question,
            'answer': self.answer,
            'comment': self.comment,
            'tip': None
        }
        result = questions.insert_one(question_data)
        logging.info(f'One question post: { result.inserted_id }')


class CurrentQuestion:
    """ Represents a current question drawn from a db """
    def __init__(self):
        questions = db.questions
        self.current_question = questions.find_one()

    @property
    def question(self):
        if self.current_question:
            return self.current_question['question']
        else:
            return None

    @property
    def answer(self):
        if self.current_question:
            return self.current_question['answer']
        else:
            return None

    @property
    def comment(self):
        if self.current_question:
            return self.current_question['comment']
        else:
            return None

    @property
    def tip(self):
        return self.current_question['tip']


def change_question_by_number(qid, question_property, text):

    questions = db.questions

    if question_property in ['question', 'answer', 'comment', 'tip']:  # защита от дурака типа меня
        result = questions.find_one_and_update({"_id": ObjectId(qid)},
                                               {'$set': {question_property: text}},
                                               return_document=ReturnDocument.AFTER)

        logging.info(f'{question_property} is changed to {text}')
        logging.info(f'One question updated. {result}')


def get_all_questions():
    all_items = list(db.questions.find())
    questions = []
    for item in all_items:
        questions.append([item['_id'], item['question'], item['answer'], item['comment'], item['tip']])
    return questions


def drop_the_db():
    """ wreck the tree and blame the doggie falalalala lala lala"""
    db.questions.remove({})


def delete_one_question(qid):
    db.questions.delete_one({"_id": ObjectId(qid)})


def close_current_question():
    question = db.questions.find_one()
    logging.info(f'Closing question: { question }...')
    answered = db.answered_users.find()

    users = []
    for user in answered:
        logging.info(f'Answered user: {user}')
        users.append(user)

    archive = db.archive
    archive.update_one({'question': question['question']}, {'$setOnInsert': {'question': question,
                                                                             'answered_users': users}}, upsert=True)
    db.questions.delete_one({})


def check_archive():
    archive = db.archive
    data = archive.find()
    return data


def get_last_winners():
    archive = db.archive
    last_question_answered = archive.find().skip(db.archive.count() - 1)
    answered_users = last_question_answered.__getitem__(0)['answered_users']
    uids = []
    for user in answered_users:
        uids.append(user['uid'])
    return uids
