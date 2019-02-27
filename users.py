from db import db
import logging


def save_user(message):
    """
    Fills a collection of all users subscribed (id, username, first name).
    """
    uid = message.chat.id
    username = message.chat.username
    first_name = message.chat.first_name

    all_users = db.all_users
    user_data = {
        'uid': uid,
        'username': username,
        'first_name': first_name
    }
    result = all_users.update_one({'uid': uid}, {'$setOnInsert': user_data}, upsert=True)
    logging.info(f'{username} started answering.')

    return user_data


def add_answering_person(message):
    """
    Adds a person (id & username) who's requested a question as one who's trying to answer,
    to a corresponding collection. Uses mongo's update() method with upsert parameter set to True.
    """
    uid = message.chat.id
    username = message.chat.username

    answering_users = db.answering_users
    user_data = {
        'uid': uid,
        'username': username,
    }
    result = answering_users.update_one({'uid': uid}, {'$setOnInsert': user_data}, upsert=True)
    logging.info(f'{username} started answering.')


def move_to_answered(chat):
    """
    Moves a person who's answered correctly to a corresponding collection.
    Uses mongo's update() method with upsert parameter set to True.
    """
    user = db.answering_users.find_one({'uid': chat.id}, {"uid": 1, "username": 1})

    result = db.answered_users.update_one({'uid': chat.id}, {'$setOnInsert': user}, upsert=True)
    db.answering_users.remove({'uid': chat.id})
    logging.info(f'Successfully moved {chat.username}')


def get_all_users_ids():
    result = []
    for document in db.all_users.find():
        result.append({
            'uid': document['uid'],
            'username': document['username']
        })
    return result


def get_answering_persons_ids():
    result = []
    for document in db.answering_users.find():
        result.append(document["uid"])
    return result


def get_answered_persons_ids():
    result = []
    for document in db.answered_users.find():
        result.append(document["uid"])
    return result


def reset_dbs():
    """
    Wreck the tree and blame the doggie falalalala lala lala
    """
    db.answering_users.remove({})
    db.answered_users.remove({})
