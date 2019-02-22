import config


def check_access(bot_function):
    def a_wrapper_accepting_arguments(message):
        print("uid:", message.chat.id)
        if message.chat.id == config.BOT_CONFIG['ADMIN_ID']:
            bot_function(message)

    return a_wrapper_accepting_arguments

