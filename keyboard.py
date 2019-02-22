from telebot import types


def create_keyboard(names, callbacks=None):
    """ takes two lists of names and corresponding callback data, and returns reply keyboard markup """

    if callbacks:
        buttons = list(zip(names, callbacks))
        keyboard = types.InlineKeyboardMarkup()

        result = []
        for button in buttons:
            text, callback_data = button
            new_button = types.InlineKeyboardButton(text=text, callback_data=callback_data)
            result.append(new_button)

        keyboard.add(*result)
        return keyboard
