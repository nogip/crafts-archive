# coding: utf-8
# Developed by nogip (Karim Mamatkazin)
# 23 August 2018 Russia, Sochi
# GitHub: github.com/nogip
# Intended for use only for legal purposes

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
        return MessageModel.select()\
            .where(MessageModel.peer_id == user_id)\
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
                offset-count+len(message_block), messages_count))

            if offset > messages_count:
                break


def init_db():
    __models__ = [UserModel, MessageModel]
    DB.create_tables(__models__, safe=True)
