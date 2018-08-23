# coding: utf-8
# Developed by nogip (Karim Mamatkazin)
# 21 August 2018 Russia, Sochi
# GitHub: github.com/nogip
# Intended for use only for legal purposes

import os
import vk_api
import datetime
from multiprocessing import Pool
from VKDatabase import MessageDownloadDBWrapper


def auth_required(func):
    def wrapper(self, *args, **kwargs):
        if 'api' in self.__dict__:
            return func(self, *args, **kwargs)
        else:
            raise vk_api.AuthError("Need login.")

    return wrapper


SEPARATE_BLOCK_SIZE = 140


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

    @auth_required
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

    @auth_required
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

    @auth_required
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

    @auth_required
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

    @auth_required
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
