import logging

from services.db import DB, DBManager
from services.models import User, Record, RecordWithUser
from config import DB_DSN, TEST_DB_DSN
from tests import querys
from tests.utilits import loads_fixtures


logging.basicConfig(format='%(asctime)s %(clientip)-15s %(user)-8s %(message)s')


class CreateTestDataBase:
    connected_db = None
    fixtures_data = None

    def setup_class(cls):
        cls.connected_db = DB(TEST_DB_DSN)
        cls.fixtures_data = loads_fixtures()
        cls._write_test_data()

    def teardown_class(cls):
        cls._delete_test_data()

    @classmethod
    def _write_test_data(cls):
        with cls.connected_db.cursor as cur:
            if cls.fixtures_data.get('users'):
                cur.executemany(querys.INSERT_USER, cls.fixtures_data.get('users'))
            if cls.fixtures_data.get('records'):
                cur.executemany(querys.INSERT_RECORD, cls.fixtures_data.get('records'))
            cls.connected_db.commit()

    @classmethod
    def _delete_test_data(cls):
        with cls.connected_db.cursor as cur:
            cur.execute("delete from records")
            cur.execute("delete from users")
            cls.connected_db.commit()


class TestDB:
    def test_connection(self):
        assert DB(DB_DSN)

    def test_open_cursor(self):
        assert DB(DB_DSN).cursor


class TestDbManager(CreateTestDataBase):
    def setup(self):
        self.manager = DBManager(TEST_DB_DSN)

    def test_get_user(self):
        data_users = TestDbManager.fixtures_data.get('users')
        for data in data_users:
            user = User(**data)
            result = self.manager.get_user(user)
            user_from_db = User(**result)
            user_from_db.id = None
            assert user == user_from_db

    def test_get_records(self):
        data = self.manager.get_records()
        for row in data:
            assert RecordWithUser(**row)

    def test_get_records_by_user(self):
        data = self.manager.get_record_by_user_id(1212)
        assert Record(**data)

        data = self.manager.get_record_by_user_id(1212, add_user_data=True)
        assert RecordWithUser(**data)
