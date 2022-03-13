import logging

from services.db import DB, DBManager
from services.models import User
from config import DB_DSN, TEST_DB_DSN
from tests import querys
from tests.utilits import loads_fixtures


logging.basicConfig(format='%(asctime)s %(clientip)-15s %(user)-8s %(message)s')


class CreateTestDataBase:
    db = None
    fixtures_data = None

    def setup_class(cls):
        cls.db = DB(TEST_DB_DSN)
        cls.fixtures_data = loads_fixtures()
        cls._write_test_data()

    def teardown_class(cls):
        cls._delete_test_data()

    @classmethod
    def _write_test_data(cls):
        with cls.db.cursor as cur:
            if cls.fixtures_data.get('users'):
                cur.executemany(querys.INSERT_USER, cls.fixtures_data.get('users'))
            if cls.fixtures_data.get('records'):
                cur.executemany(querys.INSERT_RECORD, cls.fixtures_data.get('records'))
            cls.db.commit()

    @classmethod
    def _delete_test_data(cls):
        with cls.db.cursor as cur:
            cur.execute("delete from users")
            cur.execute("delete from records")
            cls.db.commit()


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
            new_user = User(**result)
            new_user.id = None
            assert user == new_user

    def test_record(self):
        pass

