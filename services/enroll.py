import logging
from typing import Optional, List

from services import models
from services.db import DBManager


class Enroll:
    """Класс отвечающий за записи"""
    def __init__(self):
        self.db_manager = DBManager()

    def save_user(self, data: dict) -> bool:
        """сохранени и обновление данных пользователя"""
        logging.info(f'user_data = {data}')
        user = models.User(
            tg_id=data.get('id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            username=data.get('username'),
            phone=data.get('phone')
        )
        logging.info(f'user {user}')
        result = self.db_manager.get_user(user)
        logging.info(f'get_user = {result}')
        if result:
            if self._is_change_user(result, user):
                return self.db_manager.update_user(user)
            return True
        else:
            return self.db_manager.save_user(user)

    def save_record(self, user_data: dict, data: dict) -> bool:
        """сохранени и обновление данных записи"""
        if self.save_user(user_data):
            user_id = user_data.get('id')
            record = models.Record(**data, user_id=user_id)
            old_record = self.get_record(user_id)
            logging.info(f'old_record = {record}')
            if old_record:
                record.id = old_record.id
                return self.db_manager.update_record(record)
            else:
                return self.db_manager.save_record(record)
        return False

    def get_record(self, user_id: int) -> Optional[models.Record]:
        """Получение записи"""
        data = self.db_manager.get_record_by_user_id(user_id)
        if data is None:
            return None
        return models.Record(**data)

    def get_records(self) -> Optional[List[models.RecordWithUser]]:
        rows = self.db_manager.get_records()
        if rows is None:
            return None
        list_records = [models.RecordWithUser(**row) for row in rows]
        return list_records

    def get_record_with_user(self, user_id: int) -> Optional[models.RecordWithUser]:
        """Получение записи с данными пользователя"""
        data = self.db_manager.get_record_by_user_id(user_id, True)
        if data is None:
            return None
        return models.RecordWithUser(**data)

    @staticmethod
    def _is_change_user(old_data: dict, new_data: models.User) -> bool:
        """Проверка изменились ли данны пользователя"""
        if old_data is None:
            return True
        if new_data.username != old_data.get('username'):
            return True
        if new_data.last_name != old_data.get('last_name'):
            return True
        if new_data.first_name != old_data.get('first_name'):
            return True
        if new_data.phone != old_data.get('phone'):
            return True
        return False
