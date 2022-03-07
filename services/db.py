import logging
import sqlite3
import psycopg2
from datetime import datetime
from typing import Union, Optional

from services import querys, models
from config import DB_DSN


class DB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._conn = self._connect()

    def __del__(self):
        self._conn.close()

    def _connect(self):
        connect = psycopg2.connect(dsn=self.dsn)
        return connect

    def commit(self):
        self._conn.commit()

    @property
    def cursor(self):
        return self._conn.cursor()


class BaseDBManager(DB):
    def __init__(self):
        super().__init__(DB_DSN)

    def write_data(self, sql: str, params: dict):
        self.cursor.execute(sql, params)
        self.commit()

    def get_data(
            self,
            sql: str,
            params: Optional[dict] = None,
            many: bool = False
    ) -> Union[None, list, dict]:
        cur = self.cursor
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        description = cur.description

        if many:
            raw_data = cur.fetchall()
        else:
            raw_data = cur.fetchone()
        logging.info(f'raw_data = {raw_data}')
        if raw_data:
            data = self._tuple_to_dict(raw_data, description)
            return data
        return None

    @staticmethod
    def _tuple_to_dict(data: Union[list, tuple], description: tuple) -> Union[list, dict]:
        if isinstance(data[0], tuple):
            prepared_data = []
            for row in data:
                prepared_data.append(dict(tuple(zip([item[0] for item in description], row))))
            return prepared_data
        else:
            return dict(tuple(zip([item[0] for item in description], data)))


class DBManager(BaseDBManager):
    def get_user(self, user: models.User) -> dict:
        params = {
            'tg_id': user.tg_id
        }
        logging.info(f'params get_user: {params}')
        result = self.get_data(querys.GET_USER, params)
        logging.info(f'get_user result = {result}')
        return result

    def update_user(self, user: models.User) -> bool:
        try:
            params = {
                'tg_id': user.tg_id,
                'username': user.username,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'phone': user.phone
            }
            self.write_data(querys.UPDATE_USER, params)
        except sqlite3.IntegrityError as exc:
            logging.error(f'db_error exc:{exc}')
            return False
        return True

    def save_user(self, user: models.User) -> bool:
        try:
            params = {
                'tg_id': user.tg_id,
                'username': user.username,
                'last_name': user.last_name,
                'first_name': user.first_name
            }
            self.write_data(querys.SAVE_USER, params)
        except sqlite3.IntegrityError as exc:
            logging.error(f'db_error exc:{exc}')
            return False
        return True

    def save_record(self, record: models.Record) -> bool:
        """Сохранить запись на прием"""
        try:
            params = {
                "user_id": record.user_id,
                "record_date": record.record_date,
                "record_time": record.record_time
            }

            self.write_data(querys.SAVE_RECORD, params)
        except sqlite3.IntegrityError as exc:
            logging.error(f'db_error exc:{exc}')
            return False
        return True

    def update_record(self, record: models.Record):
        try:
            if record.record_date is not None:
                params = {
                    "id": record.id,
                    "record_date": record.record_date,
                    "updated_at": datetime.now()
                }
                logging.info(f'update record date params = {params}')
                self.write_data(querys.UPDATE_RECORD_DATE, params)
            elif record.record_time is not None:
                params = {
                    "id": record.id,
                    "record_time": record.record_time.strftime('%H:%M'),
                    "updated_at": datetime.now()
                }
                logging.info(f'update record time params = {params}')
                self.write_data(querys.UPDATE_RECORD_TIME, params)
            else:
                return False
        except sqlite3.IntegrityError as exc:
            logging.error(f'db_error exc:{exc}')
            return False
        return True

    def get_records(self) -> list:
        rows = self.get_data(querys.GET_RECORDS, many=True)
        logging.info(f'records = {rows}')
        return rows

    def get_record_by_user_id(self, user_id, add_user_data: bool = False) -> dict:
        start_date, end_date = self._get_start_end_date()
        params = {
            'user_id': user_id,
            'start_date': start_date,
            'end_date': end_date
        }
        logging.info(f'params = {params}')
        if add_user_data:
            row = self.get_data(querys.GET_RECORDS_WITH_USER, params)
        else:
            row = self.get_data(querys.GET_RECORDS_BY_USER_ID, params)
        logging.info(f'record = {row}')
        return row

    def get_record_event(self, record_id: int) -> dict:
        params = {
            'record_id': record_id
        }
        row = self.get_data(querys.GET_RECORD_EVENT, params)
        return row

    def save_record_event(self, record_id: int, event: str) -> bool:
        params = {
            'record_id': record_id,
            'event': event
        }
        try:
            self.write_data(querys.SAVE_RECORD_EVENT, params)
        except sqlite3.IntegrityError as exc:
            logging.error(f'error = {exc}')
            return False
        return True

    def update_record_event(self, record_id: int, event: str) -> bool:
        params = {
            'record_id': record_id,
            'event': event
        }
        try:
            self.write_data(querys.UPDATE_RECORD_EVENT, params)
        except sqlite3.IntegrityError as exc:
            logging.error(f'error = {exc}')
            return False
        return True


    @staticmethod
    def _get_start_end_date():
        now = datetime.now()
        start_date = now.replace(day=1)
        end_date = now.replace(day=30)
        return start_date, end_date


if __name__ == "__main__":
    user = models.User(
        id=None,
        tg_id=1212,
        username='pygudev',
        first_name='Евгений',
        last_name=None
    )
    DBManager().save_user(user)
