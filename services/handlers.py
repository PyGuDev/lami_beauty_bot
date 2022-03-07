import re
import logging

from datetime import date, datetime, timedelta, time
from typing import Optional

from aiogram import types

from config import OWNER
from services import models
from services.db import DBManager
from services.enroll import Enroll
from services.models import Events


class RecordEventHandler:
    """События записи"""
    def __init__(self, db_manager: DBManager):
        self._db_manager = db_manager

    def get_event(self, record_id: int) -> Optional[str]:
        """получить последние событие"""
        data = self._db_manager.get_record_event(record_id)
        if data:
            return models.RecordEvent(**data).event
        else:
            return None

    def save_event(self, record_id: int, event: str) -> bool:
        """сохранить событие"""
        record_event = models.RecordEvent(
            record_id=record_id,
            event=event
        )
        old = self.get_event(record_event.record_id)
        if old:
            if self._is_changed(old, record_event):
                self._db_manager.update_record_event(
                    record_event.record_id,
                    record_event.event
                )
        else:
            return self._db_manager.save_record_event(
                record_event.record_id,
                record_event.event
            )
        return False

    @staticmethod
    def _is_changed(old: str, new: models.RecordEvent) -> bool:
        if old != new.event:
            return True
        return False


class MainHandler(RecordEventHandler):
    """Главный класс обработчик"""
    def __init__(self, bot):
        self.bot = bot
        self.enroll = Enroll()
        super().__init__(self.enroll.db_manager)

    async def save_record_date(self, user_data: dict, selected_date: date):
        """Сохраняем запись с датой когда приходить"""
        chat_id = user_data.get('id')
        data = {'record_date': selected_date}

        enroll = Enroll()
        enroll.save_record(user_data, data)
        record = self.enroll.get_record(chat_id)
        # сохраняем событие
        self.save_event(record.id, Events.ADD_DATE)
        await self.bot.send_message(
            chat_id,
            text="Отправьте время в формате 24:00",
        )

    async def message_handler(self, message):
        """
        Обработчик который выбирает какое действие совершить
        по событию
        """
        enroll = Enroll()
        record = enroll.get_record(message.from_user.id)
        if record:
            if self.get_event(record.id) == Events.ADD_TIME:
                await self.save_user_phone(message, enroll)
            elif self.get_event(record.id) == Events.ADD_DATE:
                await self.save_record_time(message, enroll)

    async def save_record_time(self, message: types.Message, enroll: Enroll):
        """Сохраняем время когда приходить"""
        searched_time = re.search(r'^\d\d:\d\d', message.text)
        if searched_time:
            record_time = searched_time.group(0)
            record = enroll.get_record(message.from_user.id)
            if self.validate_time(record, record_time):
                data = {'record_time': record_time}
                user_data = message.from_user.values
                if enroll.save_record(user_data, data):
                    await self.bot.send_message(message.chat.id, text="Вас предворительно записали")
                    # сохраняем событие
                    record = enroll.get_record(message.from_user.id)
                    self.save_event(record.id, Events.ADD_TIME)

                    if user_data.get('username') is None:
                        await self.bot.send_message(
                            message.chat.id,
                            text="Укажите номер телефона, желательно"
                                 "чтобы он был привязан к телеграмму"
                        )
                    else:
                        updated_record = enroll.get_record_with_user(user_id=message.from_user.id)
                        await self.bot.send_message(OWNER, text=self.formatting_event_message(updated_record))
                else:
                    await self.bot.send_message(message.chat.id, text="Ошибка записи")
            else:
                await self.bot.send_message(
                    message.chat.id,
                    text="Указанное время должно быть больше текушего + 1 час")
        else:
            await self.bot.send_message(
                message.chat.id,
                text="Не правильно укзали время записи, повторите попытку")

    async def get_records(self):
        enroll = Enroll()
        records = enroll.get_records()
        if records:
            for record in records:
                text = self.formatting_record_messages(record)
                await self.bot.send_message(OWNER, text=text)
        else:
            await self.bot.send_message(OWNER, text="Никто не записывался")

    @staticmethod
    def validate_time(record, record_time: str) -> bool:
        record_time = time.fromisoformat(record_time)
        now = datetime.now()
        if record.record_date == now.date():
            diff = now + timedelta(hours=1)
            if record_time < diff.time():
                return False
            else:
                return True
        elif record.record_date < now.date():
            return False
        else:
            return True

    async def save_user_phone(self, message: types.Message, enroll: Enroll):
        """Сохраняем номер телефона клиента"""
        searched_phone = re.search('^[7-8][0-9]{10}', message.text)
        if searched_phone:
            phone = searched_phone.group(0)
            data = message.from_user.values
            data['phone'] = phone
            logging.info(f'save phone {data}')
            if enroll.save_user(data):
                updated_record = enroll.get_record_with_user(user_id=message.from_user.id)
                # сохраняем событие
                self.save_event(updated_record.id, Events.ADD_PHONE)
                await self.bot.send_message(OWNER, text=self.formatting_event_message(updated_record))

        else:
            await self.bot.send_message(
                message.chat.id,
                text="Не правильно укзали номер телефона, повторите попытку")

    @staticmethod
    def formatting_event_message(record: models.RecordWithUser) -> str:
        """Подготовка сообщения о создании записи"""
        formatted_date = record.record_date.strftime("%d.%m.%Y")
        formatted_time = record.record_time.strftime("%H:%M")
        header_sting = f"Эмилия к вам записались\n" \
                       f"На {formatted_date} в {formatted_time}\n"
        if record.username:
            items = [record.last_name, record.first_name, f'@{record.username}']
        else:
            items = [record.last_name, record.first_name, record.phone]
        user_string = " ".join(item for item in items if item is not None)

        return header_sting + user_string

    @staticmethod
    def formatting_record_messages(record: models.RecordWithUser) -> str:
        """Подготовка сообщнеий по записи"""
        formatted_date = record.record_date.strftime("%d.%m.%Y")
        formatted_time = record.record_time.strftime("%H:%M")
        header_sting = f"На {formatted_date} в {formatted_time}\n"
        if record.username:
            items = [record.last_name, record.first_name, f'@{record.username}']
        else:
            items = [record.last_name, record.first_name, record.phone]
        user_string = " ".join(item for item in items if item is not None)

        return header_sting + user_string
