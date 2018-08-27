# coding: utf-8
# Developed by nogip (Karim Mamatkazin)
# 21-23 August 2018 Russia, Sochi
# GitHub: github.com/nogip
# Intended for use only for legal purposes

import os
import vk_api
import datetime
from multiprocessing import Pool
from VKDatabase import MessageDownloadDBWrapper

SEPARATE_BLOCK_SIZE = 140
YEAR = 31536000


class VKManage:
    # Need follow imports:
    # os, datetime, multiprocessing.dummy.Pool, vk_api

    # Поскольку сохранение ВСЕХ сообщений может занимать много времени,
    # а для их протоколирования требуется много действий
    # сначала происходит сохранение всех сообщений в database,
    # и уже после этого составлять протокол для каждого собеседника в отдельном процессе.
    # Чертов GIL

    # ? : Wrapper для обновления дб
    # ? : Подогнать существующий код для использования бд

    SEPARATOR = " - "

    TIME_SETTING = '^10'
    NAME_SETTING = '>25'
    BLANK_SETTING = '<36'

    POSTFIX = '*'

    NEW_LINE = '\n'
    if os.name == 'nt':
        NEW_LINE = '\r\n'

    FORMAT_ARGS = {
        'time_setting': TIME_SETTING,
        'name_setting': NAME_SETTING,
        'blank_size': BLANK_SETTING,
        'separator': SEPARATOR,
        'postfix': POSTFIX,
        'nl': NEW_LINE
    }

    def __init__(self, login, password, db_wrap=None, debug=False, max_workers=20, v=0):
        self.verbose = v
        self.debug = debug
        self.db = db_wrap
        self.vk = vk_api.VkApi(login, password)
        self._max_worker_threads = max_workers

        self.__name__ = 'VKManage'
        self.count_all_deleted = 0

    # ///////////////// Save Messages /////////////////

    def log(self, *msgs, v=1):
        if self.debug and v <= self.verbose:
            print('{} |'.format(self.__name__), *msgs)

    def get(self, key):
        return self.__getattribute__(key)

    def auth(self):
        try:
            self.vk.auth()
            self.api = self.vk.get_api()
            if self.db:
                self.db = self.db(self.api, v=self.verbose, debug=self.debug)
            info = self.api.users.get()[0]
            self.uid = info.get('id')
            self.first_name = info.get('first_name')
            self.last_name = info.get('last_name')
            self.full_name = '{}_{}'.format(self.first_name, self.last_name)
            self.log('{nl}Login successful{nl}'.format(nl=self.NEW_LINE))
            self._create_storage_dir()
            return True
        except vk_api.AuthError:
            return False

    def _create_storage_dir(self):
        self.save_dir = os.path.join(os.getcwd(), self.full_name)
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

    def _get_dialogs_ids(self):
        # Получение id всех диалогов
        dialogs = []
        items = self.api.messages.getDialogs().get('items')
        for dialog in items:
            message = dialog.get('message')
            user_id = message.get('user_id')
            if int(user_id) < 0:
                continue
            dialogs.append(user_id)
        return dialogs

    def send(self, msg, user_id=None):
        if not user_id:
            user_id = self.uid
        if msg:
            self.api.messages.send(user_id=user_id, message=msg)
        self.log('[+] Sent report --> {}'.format(user_id))

    def dump_dialogs(self):
        user_ids = self._get_dialogs_ids()
        if len(user_ids) > self._max_worker_threads:
            workers = self._max_worker_threads
        else:
            workers = len(user_ids)
        p = Pool(workers)
        self.save_dialogs_db(user_ids)

        # Не передаем downloader в аргументах потому что увеличится сложность.
        # Тогда в функции для map нужно проверять, определена ли обертка
        # для скачивания сообщений при создании экземпляра данного класса.
        # p.map(self.create_report, user_ids)

        for uid in user_ids:
            self.create_report(uid)

    def save_dialogs_db(self, *args):
        if not self.db:
            raise RuntimeError('Database not initialized.')
        for uid in self._get_dialogs_ids():
            self.db.download_msgs_with(uid)
        self.log('[+] All chats downloaded.')

    @staticmethod
    def parse_attachments(attachments):
        parsed_attachments = []
        for attach in attachments:
            attach_type = attach.get('type')
            item = attach.get(attach_type)
            if not item:
                continue

            if attach_type in ['doc', 'audio', 'link']:
                url = item.get('url')

            elif attach_type == 'photo':
                if 'sizes' in item:
                    url = item.get('sizes')[-1].get('url')
                else:
                    if 'photo_1920' in item:
                        url = item.get('photo_1920')
                    elif 'photo_1280' in item:
                        url = item.get('photo_1280')
                    elif 'photo_604' in item:
                        url = item.get('photo_604')
                    elif 'photo_130' in item:
                        url = item.get('photo_130')
                    else:
                        url = 'undefined :c'

            elif attach_type == 'video':
                owner_id = item.get('owner_id')
                item_id = item.get('id')
                url = 'https://vk.com/{at}{oid}_{iid}'.format(at=attach_type, oid=owner_id, iid=item_id)

            elif attach_type == 'sticker':
                url = item.get('images')[-1].get('url')

            else:
                url = ''

            if url:
                parsed_attachments.append((attach_type, url))
        return parsed_attachments

    @staticmethod
    def split_text_by_count(text, max_size=60):
        # Примитивная реализация перевода строк
        if not text:
            return []

        if len(text) <= max_size:
            return [text, ]

        splited_text = text.split()
        result = []

        sym_counter = 0
        row = ''
        while splited_text:
            part = splited_text.pop(0)
            sym_counter += len(part) + 1
            row += ' ' + part
            if sym_counter > max_size:
                result.append(row.lstrip())
                sym_counter = 0
                row = ''
        return result

    # Этот метод занимает очень много времени
    # Подозреваю, что это связано с сетевыми запросами.
    # Теперь все вложения будут сохраняться в базе данных

    def create_report(self, contact_id, count=200):
        # Дамп чата
        if self.db:
            contact_info = self.db.get_user(user_id=contact_id)
        else:
            contact_info = self.api.users.get(user_ids=contact_id)[0]
        contact_fullname = '{}_{}'.format(contact_info.get('first_name'), contact_info.get('last_name'))

        storage_path = os.path.join(self.save_dir, 'messages')
        if not os.path.exists(storage_path):
            os.mkdir(storage_path)

        chat_file_path = os.path.join(storage_path, contact_fullname + '.txt')
        chat_file = open(chat_file_path, 'ab')
        self.log('({}) open chatfile [{}]'.format(contact_id, chat_file_path))

        # Метод получает блок сообщений, записывает их и запрашивает еще, пока не получит все.
        if self.db:
            storage = self.db
            messages_count = storage.count_messages(contact_id)
        else:
            storage = self.api.messages
            messages_count = self.api.messages.getHistory(contact_id, count=1).get('count')
        offset = 0
        while True:
            if self.db:
                message_block = storage.getHistory(contact_id)
            else:
                message_block = storage.getHistory(contact_id, count=count, offset=offset, rev=1).get('items')
            offset += count
            last_date = None
            for message in message_block:
                heading_pattern = \
                    "{nl}{fill:10}  {date} | {owner} <-> {contact} | " \
                    "[{owner_id} <-> {contact_id}]  {fill:10}{nl}{nl}"
                date = datetime.datetime.fromtimestamp(message.get('date'))
                if last_date != date.date():
                    last_date = date.date()
                    heading = heading_pattern.format(
                        owner=self.full_name, owner_id=self.uid,
                        contact=contact_fullname, contact_id=contact_id,
                        date=last_date.isoformat(),
                        fill='+' * 15, nl=self.NEW_LINE).upper()
                    chat_file.write(heading.encode())

                chat_file.write(self.convert_message(message).encode())
                self.log('[+] [{}] message written.'.format(contact_fullname), v=2)
            self.log('[+] [{}] block ({}/{}) written.'.format(contact_fullname, offset, messages_count), v=1)
            if offset > messages_count:
                break

        chat_file.close()
        self.log('[+] ({}) {} finished.'.format(contact_id, contact_fullname))

    def convert_message(self, message):
        text = message.get('text')
        date = datetime.datetime.fromtimestamp(message.get('date'))
        fwd_messages = message.get('fwd_messages')
        attachments = message.get('attachments')

        if isinstance(attachments, bool) or isinstance(fwd_messages, bool):
            additions = self.api.messages.getById(message_ids=message.get('id')).get('items')[0]
            if attachments:
                attachments = additions.get('attachments')
            if fwd_messages:
                fwd_messages = additions.get('fwd_messages')

        blank = '{blank:{blank_size}}'.format(blank='', blank_size=self.BLANK_SETTING)

        if message.get('from_id') != self.uid:
            if self.db:
                contact_info = self.db.get_user(user_id=message.get('from_id'))
            else:
                contact_info = self.api.users.get(user_ids=message.get('from_id'))[0]
        else:
            contact_info = self

        # Настройки для сообщения
        format_args = self.FORMAT_ARGS.copy()
        format_args.update({
            'name': self.full_name if not contact_info
            else '{}_{}'.format(contact_info.get('first_name'), contact_info.get('last_name')),
            'time': date.time().isoformat()[:-3],
        })

        # Создание строк сообщения
        text_row = ''
        text_first_pattern = '{time:{time_setting}} {name:{name_setting}}{separator}{text} {nl}'
        if text:
            text_more_pattern = blank + '{separator}{text} {nl}'

            first_saved = False
            for block in self.split_text_by_count(text):
                format_args.update({'text': block})
                if not first_saved:
                    use_pattern = text_first_pattern
                    first_saved = True
                else:
                    use_pattern = text_more_pattern
                text_row += use_pattern.format(**format_args)
        else:
            format_args.update({'text': ' -' * 10})
            text_row += text_first_pattern.format(**format_args)

        # Сначала обрабатываются вложения основного сообщения
        # потом пересланных сообщений
        attach_row = ''
        if attachments:
            attachments_pattern = blank + '{separator}{attach} {nl}'
            attachments = self.parse_attachments(attachments)
            for attach in attachments:
                attach = '{}: {}'.format(attach[0].upper(), attach[1])
                attach_row += attachments_pattern.format(attach=attach, **format_args)

        # Создание строк для пересланых сообщений
        fwd_row = ''
        if fwd_messages:
            fwd_row = self.convert_forwarded(fwd_messages).rstrip(self.NEW_LINE) + self.NEW_LINE

        return text_row + attach_row + fwd_row

    def convert_forwarded(self, fwd_messages_list, nesting=1):
        if not fwd_messages_list:
            return

        if isinstance(fwd_messages_list, dict):
            fwd_messages_list = list(fwd_messages_list)

        nesting_level = ' |' * nesting
        blank = '{blank:{blank_size}}'.format(blank='', blank_size=self.BLANK_SETTING)

        fwd_format_args = self.FORMAT_ARGS.copy()
        fwd_format_args.update({'name_setting': '<', 'time_setting': '^20'})

        fwd_participants_names = {self.uid: self.full_name}
        fwd_row = ''

        # patterns
        forward_heading_pattern = blank + nesting_level + '{time:{time_setting}}{name:{name_setting}} {nl}'
        forward_content_pattern = blank + nesting_level + '{forward} {nl}'
        attachments_pattern = blank + nesting_level + '{attach} {nl}'

        for fwd_message in fwd_messages_list:
            from_id = fwd_message.get('from_id')

            # Запрашиваем информацию о пользователях в пересланных сообщениях
            # Если уже запросили информацию, то не запрашиваем снова
            if from_id not in fwd_participants_names:
                fwd_participant = self.api.users.get(user_ids=from_id)[0]
                fwd_participant_fullname = '{} {}'.format(
                    fwd_participant.get('first_name'), fwd_participant.get('last_name'))
                fwd_participants_names.update({from_id: fwd_participant_fullname})

            # Настройка заголовка
            # Имя отправителя и дата
            fwd_date = datetime.datetime.fromtimestamp(fwd_message.get('date'))
            fwd_format_args.update({
                'name': fwd_participants_names.get(from_id), 'time': fwd_date.isoformat(' ')[:-3]})

            fwd_row += forward_heading_pattern.format(**fwd_format_args)

            # Создаем строку с текстом сообщения
            fwd_text = fwd_message.get('text')
            for block in self.split_text_by_count(fwd_text):
                fwd_format_args.update({'forward': block})
                fwd_row += forward_content_pattern.format(**fwd_format_args)

            # Создаем строку со ссылками на вложения
            fwd_attachments = fwd_message.get('attachments')
            if fwd_attachments:
                fwd_attachments = self.parse_attachments(fwd_attachments)
                for attach in fwd_attachments:
                    attach = '{} {}'.format(attach[0].upper(), attach[1])
                    fwd_row += attachments_pattern.format(attach=attach, **fwd_format_args)

            # Проверяем есть ли еще пересланые сообщения в данном
            # Если есть, то рекурсивно добавляем вложенные сообщения
            # Уровень вложенности +1
            fwd_forward_messages = fwd_message.get('fwd_messages')
            if fwd_forward_messages:
                fwd_row += self.convert_forwarded(fwd_forward_messages, nesting + 1)

            fwd_row += '{nl}'.format(nl=fwd_format_args.get('nl'))
        return fwd_row

    def _delete_comment(self, owner_id, comment_id):
        status = self.api.wall.deleteComment(owner_id=owner_id, comment_id=comment_id)
        if status:
            self.count_all_deleted += 1
        else:
            self.log("[-] Не удалено {}_{}".format(owner_id, comment_id), v=2)
        return status

    def delete_comments_in_group(self, group_id, count=100, end_date=None, years=1):
        if not end_date:
            end_date = datetime.datetime.now().timestamp() - float(YEAR * years)
        group_info = self.api.groups.getById(group_ids=abs(group_id))[0]
        deleted_count = 0
        loop = True
        offset = 0
        msg = '[!] Start cheking group ({})'.format(group_info.get('name'))
        self.log(msg)
        self.send(msg)
        cant_post = 0
        patient_level = 5
        while loop:
            posts = self.api.wall.get(owner_id=group_id, offset=offset, count=count).get('items')
            offset += count
            for post in posts:

                if not post.get('comments').get('can_post'):
                    cant_post += 1

                if cant_post == patient_level:
                    self.log('[!] Group does not provide commenting.')
                    loop = False
                    break

                if post.get('date') >= end_date:
                    deleted_count += self.delete_comments_in_post(post.get('from_id'), post.get('id'))
                else:
                    loop = False
                    break
        msg = '[!] group ({}) checked. Deleted ({}).'.format(group_info.get('name'), deleted_count)
        self.log(msg)
        self.send(msg)

    def clear_newsfeed(self, count=100):
        """
        Метод нужен для получения списка id всех постов,
        в которых пользователь оставил комментарий.

        До тех пор, пока количество полученных постов равно @count,
        продолжать запрашивать данные.
        Иначе, задать флаг @loop в False чтобы остановить цикл запроса.
        """
        start_from = None
        filtered_posts = []

        loop = True
        while loop:
            response = self.api.newsfeed.getComments(count=count, start_from=start_from)
            start_from = response.get('next_from')
            posts = response.get('items')
            if len(posts) < count:
                loop = False
            for post in posts:
                post_id = post.get('post_id')
                source_id = post.get('source_id')
                filtered_posts.append((source_id, post_id))
        return filtered_posts

    def delete_comments_in_post(self, source_id, post_id, count=100):
        # source_id = (src_id * -1)
        offset = 0
        group_deleted = 0
        count_comments = -1
        # group_name = self.api.groups.getById(group_id=source_id)[0].get('name')

        try:
            count_comments = self.api.wall.getComments(owner_id=source_id, post_id=post_id).get('count')
        except vk_api.ApiError:
            print('Something went wrong / https://vk.com/topic{}_{}?offset=400'.format(source_id, post_id, offset))

        self.log('[ ] ({}) post ({})'.format(source_id, post_id), v=2)
        while offset <= count_comments:
            try:
                comments = self.api.wall.getComments(
                    count=count, owner_id=source_id, post_id=post_id, offset=offset).get('items')
                offset += count
                for comment in comments:
                    if self.uid == comment.get('from_id'):
                        comment_id = comment.get('id')
                        deleted = self._delete_comment(owner_id=source_id, comment_id=comment_id)
                        if deleted:
                            group_deleted += 1
                            self.log('[+] ({}) from [{}] deleted.'.format(comment_id, source_id), v=2)
            except vk_api.ApiError:
                print('Something went wrong / https://vk.com/topic{}_{}?offset=400' \
                      .format(source_id, post_id, offset))
        return group_deleted

    def delete_comments(self, parallel=False, years=1):
        groups = [x * -1 for x in self.api.groups.get(user_id=self.uid).get('items')]
        if parallel:
            if len(groups) > self._max_worker_threads:
                workers = self._max_worker_threads
            else:
                workers = len(groups)
            p = Pool(workers)
            p.map(self.delete_comments_in_group, groups)
            p.join()
        else:
            checked_write = open('checked.txt', 'a')
            checked_read = open('checked.txt', 'r')
            for row in checked_read.readlines():
                if row in groups:
                    groups.remove(int(row.strip()))
            for group in groups:
                self.delete_comments_in_group(group, years=years)
                checked_write.write(str(group))


from peewee import *

DB = SqliteDatabase('vkmanage.db')


class User:

    def __init__(self, id=None, api=None):
        self.id = id
        self.api = api

    def fill(self):
        if not self.id:
            raise RuntimeWarning('Define user id as uid.')
        if not self.api:
            raise RuntimeWarning('Not defined api.')
        fields = 'domain, sex, bdate, contacts'
        return self.set_props(self.api.users.get(user_ids=self.id, fields=fields)[0])

    def set_props(self, user_props):
        if not isinstance(user_props, dict):
            raise TypeError('User properties should be a dict.')
        for prop in user_props:
            self.__setattr__(prop, user_props.get(prop))
        return self

    def fullname(self):
        if 'first_name' and 'last_name' in self.__dict__:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            raise RuntimeWarning('User has not been initialized.')

    def get(self, key):
        return self.__getattribute__(key)

    def __repr__(self):
        info = ''
        for key, value in self.__dict__.items():
            info += '[{}]: ({})\r\n'.format(key, value)
        return info

    def __eq__(self, other):
        for key in self.__dict__:
            if not self.__getattribute__(key) == other.__getattribute__(key):
                return False
        return True


class UserModel(Model):
    id = BigIntegerField(primary_key=True, index=True, unique=True)
    first_name = CharField()
    last_name = CharField()
    sex = IntegerField(null=True)
    domain = CharField(null=True)
    bdate = CharField(null=True)
    mobile_phone = CharField(null=True)
    home_phone = CharField(null=True)
    role = CharField(null=True)

    class Meta:
        db_table = "User"
        database = DB

    @staticmethod
    def count():
        return len(UserModel.get_Users_ids())

    @staticmethod
    def add_user(user):
        try:
            UserModel.create(**user.__dict__)
        except IntegrityError as err:
            print('[!] INSERT FAILED: [id={}] \n[!] Error: {}'.format(user.id, err))

    @staticmethod
    def delete_user(user_id):
        delete = UserModel.delete().where(UserModel.id == user_id)
        delete.execute()

    @staticmethod
    def get_user(user_id, *args):
        user = UserModel.select(*args).where(UserModel.id == user_id).get()
        return user

    # 2-Male 1-Female 0-All
    @staticmethod
    def get_users(admins=False, editors=False, moders=False, sex=0, only_ids=False):
        if sex == 1:
            query = UserModel.select().where(
                UserModel.sex == sex)

        elif sex == 2:
            query = UserModel.select().where(
                UserModel.sex == sex)

        else:
            if admins:
                query = UserModel.select().where(
                    (UserModel.role == 'administrator') |
                    (UserModel.role == 'creator'))
            elif editors:
                query = UserModel.select().where(
                    UserModel.role == 'editor')
            elif moders:
                query = UserModel.select().where(
                    UserModel.role == 'moderator')
            else:
                query = UserModel.select()

        if only_ids:
            return [user.id for user in query]
        else:
            return query

    @staticmethod
    def getHistory(user_id):
        return MessageModel.select() \
            .where(MessageModel.peer_id == user_id) \
            .order_by(MessageModel.date).dicts()


class Message:
    # Вложения сохранять не имеет смысла
    # потому что они могут повторяться из сообщения в сообщение.
    # Считаю более выгодным сохранять факт их наличия
    # и при необходимости делать запрос к Api
    def fill(self, msg_dict):
        if not isinstance(msg_dict, dict):
            raise TypeError('Message props must be in a dict')

        for key, value in msg_dict.items():
            if key in ['fwd_messages', 'attachments']:
                self.__setattr__(key, True) if value else self.__setattr__(key, False)
            else:
                self.__setattr__(key, value)
        return self

    def __repr__(self):
        return '[from: {}] [text: {}]'.format(self.from_id, self.text)


class MessageModel(Model):
    date = BigIntegerField()
    from_id = BigIntegerField()
    id = BigIntegerField(primary_key=True, unique=True)
    out = IntegerField()
    peer_id = ForeignKeyField(UserModel, index=True)
    text = CharField(null=True)
    conversation_message_id = BigIntegerField()
    fwd_messages = BooleanField(default=False)
    important = BooleanField(default=False)
    random_id = BigIntegerField(default=0)
    attachments = BooleanField(default=False)

    class Meta:
        db_table = "Message"
        database = DB

    @staticmethod
    def add_message(message):
        try:
            MessageModel.create(**message.__dict__)
        except IntegrityError as err:
            print('[!] INSERT FAILED: [id={}]. \n[!] Error: {}'.format(message.id, err))
            pass


def api_reqiured(func):
    def wrapper(self, *args, **kwargs):
        if self.__dict__.get('api'):
            return func(self, *args, **kwargs)
        else:
            raise RuntimeWarning("Api required.")

    return wrapper


class MessageDownloadDBWrapper:

    def __init__(self, api=None, debug=False, v=0):
        self.__name__ = 'MessageDownloadDBWrapper'
        self.api = api
        self.info = self.api.users.get()[0]
        self.verbose = v
        self.debug = debug
        init_db()

    def log(self, *msgs, v=1):
        if self.debug and v <= self.verbose:
            print('{} |'.format(self.__name__), *msgs)

    @staticmethod
    def get_user(user_id):
        for prop in UserModel.select().where(UserModel.id == user_id).dicts():
            return User().set_props(prop)

    @staticmethod
    def getHistory(contact_id, *args, **kwargs):
        return UserModel.getHistory(contact_id)

    @staticmethod
    def count_messages(contact_id):
        return len(MessageModel.select().where(MessageModel.peer_id == contact_id))

    @api_reqiured
    def add_user(self, user):
        if isinstance(user, User):
            UserModel.add_user(user)
        elif isinstance(user, int):
            usr = User(user, api=self.api).fill()
            UserModel.add_user(usr)
        else:
            print('[!] WRONG FORMAT: add_user argument must be user id or User instance.')
            return False

    @api_reqiured
    def download_msgs_with(self, contact_id, count=200, **kwargs):
        messages_count = self.api.messages.getHistory(user_id=contact_id, count=1).get('count')
        offset = 0
        contact = self.api.users.get(user_ids=contact_id)[0]
        self.add_user(contact_id)
        while True:
            message_block = self.api.messages.getHistory(user_id=contact_id, count=count, **kwargs).get('items')
            offset += count
            for message in message_block:
                # Type checker здесь ругается на то,
                # что объект сообщения не имеет нужного атррибута.
                # Однако, если передать сюда message от api без изменений,
                # то все нужные аттрибуты будут в наличии.
                MessageModel.add_message(Message().fill(message))
            self.log('[+] ({} {}) Block written ({}/{})'.format(
                contact.get('first_name'), contact.get('last_name'),
                offset - count + len(message_block), messages_count))

            if offset > messages_count:
                break


def init_db():
    __models__ = [UserModel, MessageModel]
    DB.create_tables(__models__, safe=True)


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 4:
        vkmanage = VKManage(sys.argv[1], sys.argv[2], db_wrap=MessageDownloadDBWrapper, v=2, debug=bool(1))
        vkmanage.auth()
        vkmanage.delete_comments(years=sys.argv[3])
        vkmanage.send('[+] Exit.')
