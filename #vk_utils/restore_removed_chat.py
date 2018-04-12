import vk_api

login = input('Your login:\n')
password = input('Enter your password:\n')

COUNT = 2000
MESSAGE = '.'
chat_default = 2000000000

# ids = int(input('Range of ids?\n'))
# chat_title = input('Chat title?\n')

vk = vk_api.VkApi(login, password)
vk.auth()

my_id = vk.method('users.get')[0].get('id')
end_of_input = '{msg} (через пробел)\nЧтобы выйти -> Enter\n'


def list_chats():
    for chat in range(1, COUNT):
        try:
            response = dict(vk.method('messages.getChat', {'chat_id': chat}))
            print('{0:3} - {1}'.format(chat, response.get('title')))
        except:
            break
    print('-' * 40)

    chats = input(end_of_input.format(msg='Выберите чаты')).split()
    if len(chats) > 1:
        return list(map(int, chats))
    else:
        return int(chats[0])


def find_chat():
    chat_title = input('Название беседы >> ')
    for id in range(1, COUNT):
        response = dict(vk.method('messages.getChat', {'chat_id': id}))
        if chat_title in response.get('title'):
            chat_id = int(response.get('id'))
            return_in_chat(chat_id)


def return_in_chat(chat_id, msg='.'):
    chat_id = chat_default + int(chat_id)
    if input('Return to the chat? (y/n)\n') in ['y', 'Y', 'yes']:
        vk.method('messages.send', {
            'peer_id': chat_id,
            'message': msg})
        print('Successful returned to {}'.format(chat_id))
    else:
        print('Returning cancelled')


def clear_chat(chat_id, offset=200, block_size=200, del_for_all=True, one_loop=False):
    if not input('Really delete all your messages? (y/n)\n') in ['y', 'Y', 'yes']:
        return

    local_offset = 0
    chat_id = chat_default + int(chat_id)
    count = vk.method('messages.getHistory', {'peer_id': chat_id}).get('count')
    while local_offset < count:
        mes_to_del = ''
        messages = vk.method('messages.getHistory', {
            'peer_id': chat_id,
            'count': block_size,
            'offset': local_offset}).get('items')
        local_offset += offset

        exist_in_block = 0
        for message in messages:
            if message.get('user_id') == my_id:
                mes_to_del += '{},'.format(message.get('id'))
                exist_in_block = 1
        if exist_in_block == 1:
            try:
                response = vk.method('messages.delete', {
                    'message_ids': mes_to_del,
                    'delete_for_all': del_for_all})
                print("Messages deleted", response)
                if one_loop: break
            except vk_api.exceptions.ApiError:
                # print("Messages with id {} were not deleted".format(mes_to_del))
                continue


def main():
    print('Login successful...\n')
    how_find = int(input('Как найти беседу?\n 1) Список всех бесед\n 2) Найти по названию\n>> '))
    action = int(input('Что сделать?\n 1) Вернуться в чат\n 2) Очистить чат\n>> '))

    if how_find == 1:
        meth_func = list_chats
    else:
        meth_func = find_chat
        # should ask a conferrence title

    if action == 2:
        action_func = clear_chat
    else:
        action_func = return_in_chat

    returns = meth_func()
    if returns:
        if isinstance(returns, list):
            for chat_id in returns:
                action_func(chat_default + int(chat_id))
        else:
            action_func(returns)
    return


if __name__ == '__main__':
    main()
