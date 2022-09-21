# pylint: disable=E0402,E0401,E0611,C0412

import sqlite3
from fastapi import HTTPException
from models.database import User
from helpers.database import DatabaseHelper
from helpers.log import LogHelper
from helpers.user import UserHelper
from config.config import Config
from helpers.auth import AuthHelper
from models import request
from utils import validate_index_pattern
import main
import pytest

databaseHelper = DatabaseHelper(Config.DATABASE_PATH)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)
logHelper = LogHelper(databaseHelper)
userHelper = UserHelper(databaseHelper)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want

    yield  # this is where the testing happens

    # Teardown : fill with any logic you want

    con, cur = databaseHelper.get_database_connection()

    delete_user_password_sql = """
        DELETE FROM user WHERE username = ?
    """

    cur.execute(delete_user_password_sql,
                ('newuser',))

    cur.execute('DELETE FROM field')
    cur.execute('DELETE FROM log')
    cur.execute('DELETE FROM log_index')

    con.commit()

    con.close()


class TestAuth:

    # Auth::correct_password

    def test_correct_password_valid(self):

        # SHA256 hash of 'password'
        password_hash = '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'
        assert authHelper.correct_password(password_hash, 'password') is True

    def test_correct_password_invalid(self):
        # SHA256 hash of 'password'
        password_hash = 'ww'
        assert authHelper.correct_password(password_hash, 'password') is False

    # Auth::authenticate_user.

    def test_authenticate_user_correct_details(self):

        user = authHelper.authenticate_user('testuser', 'password')

        # pylint: disable=E1101
        assert user.username == 'testuser'

    def test_authenticate_user_wrong_password(self):

        user = authHelper.authenticate_user('testuser', 'password1')

        assert user is False

    def test_authenticate_user_wrong_username(self):

        user = authHelper.authenticate_user('testuser2', 'password')

        assert user is False

    # Auth::get_user

    def test_get_user_valid(self):

        user = authHelper.get_user('testuser')

        assert user.username == 'testuser'

    def test_get_user_invalid(self):

        user = authHelper.get_user('no')

        assert user is None


class TestUser:

    # User::create_new_user

    def test_create_new_user_valid(self):

        # Insert new user with method to test

        userHelper.create_new_user('newuser', 'passwordhash', 1, 1)

        # Grab our newly created user
        user = authHelper.get_user('newuser')

        assert user.username == 'newuser'

    def test_create_new_user_invalid_params(self):

        # Insert new user with method to test

        assert userHelper.create_new_user(
            'newuser', 'passwordhash', 7, 7) is False

    # User::update_password

    def test_update_password_valid(self):
        # Insert new user with method to test

        new_password = 'password'

        userHelper.update_password('testuser', new_password)

        # Grab our newly created user
        user = authHelper.get_user('testuser')

        assert user.password == new_password

    # User::delete_user

    def test_delete_user(self):
        userHelper.create_new_user('newuser', 'passwordhash', 1, 1)

        userHelper.delete_user('newuser')

        assert authHelper.get_user('newuser') is None


class TestLog:

    # Log::ingest_log

    def test_ingest_log(self):

        con, cur = databaseHelper.get_database_connection()

        cur.execute(
            "INSERT INTO log_index VALUES ('testindex',julianday('now'), julianday('now'), 1 )")
        con.commit()
        con.close()

        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        assert len(logHelper.retrieve_index('testindex')) == 2

    def test_ingest_log_no_index(self):

        with pytest.raises(sqlite3.IntegrityError) as err:

            logHelper.ingest_log('testindex', 'testsource', {
                'time': '2022-10-08', 'message': 'This is a test message!'})

        assert err

    # Log::create_index and retrieve_all_indexes

    def test_create_index_valid(self):
        res = logHelper.create_index('testindex', 1)
        index = logHelper.retrieve_all_indexes()
        print(index)
        assert index[0]['name'] == 'testindex'

    def test_create_index_invalid(self):

        with pytest.raises(sqlite3.IntegrityError) as err:

            logHelper.create_index('testindex', 9)
        assert err

    # Log::retrieve_index

    def test_retrieve_index(self):
        logHelper.create_index('testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        # Delete timestamps as can never be the same
        res = logHelper.retrieve_index('testindex')
        for k in res:
            del k['timestamp']

        assert res == [{'index_name': 'testindex', 'field': 'time', 'message': '2022-10-08', 'source': 'testsource'}, {
            'index_name': 'testindex', 'field': 'message', 'message': 'This is a test message!', 'source': 'testsource'}]

    def test_retrieve_index_not_existing(self):

        # Delete timestamps as can never be the same
        assert logHelper.retrieve_index('testindex') is False

    # Log::create_if_not_exists

    def test_index_if_exists_does(self):
        logHelper.create_index('testindex', 1)

        assert logHelper.create_if_not_exists('testindex', 1) is False

    def test_index_if_exists_does_not(self):
        assert len(logHelper.create_if_not_exists('testindex', 1)) == 4

    # Log::retrieve_by_index_pattern

    def test_retrieve_by_index_pattern_end(self):

        logHelper.create_index('testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        logHelper.create_index('testindex1', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        assert len(logHelper.retrieve_index_by_pattern('testindex%')) == 4

    def test_retrieve_by_index_pattern_start(self):

        logHelper.create_index('testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        logHelper.create_index('1testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        assert len(logHelper.retrieve_index_by_pattern("%index")) == 4

    def test_retrieve_by_index_pattern_both(self):

        logHelper.create_index('testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        logHelper.create_index('1testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        assert len(logHelper.retrieve_index_by_pattern("%tin%")) == 4

    # Log::DeleteIndex

    def test_delete_index(self):

        logHelper.create_index('testindex', 1)
        logHelper.ingest_log('testindex', 'testsource', {
                             'time': '2022-10-08', 'message': 'This is a test message!'})

        logHelper.delete_index('testindex')

        assert logHelper.retrieve_index('testindex') is False


class TestUtils:

    # Utils::validate_index_pattern

    def test_validate_index_pattern_valid_end(self):

        index_pattern, err = validate_index_pattern("test*")

        assert err is None and index_pattern == "test%"

    def test_validate_index_pattern_valid_start(self):

        index_pattern, err = validate_index_pattern("*test")

        assert err is None and index_pattern == "%test"

    def test_validate_index_pattern_valid_middle(self):

        index_pattern, err = validate_index_pattern("*test*")

        assert err is None and index_pattern == "%test%"

    def test_validate_index_pattern_invalid_no_asteriks(self):

        index_pattern, err = validate_index_pattern("test")

        assert err == "Index Pattern must contain asterisk" and index_pattern == "test"

    def test_validate_index_pattern_invalid_in_middle(self):

        index_pattern, err = validate_index_pattern("te*st")

        assert err == "Wildcards must be at the start and end." and index_pattern == "te%st"

    def test_validate_index_pattern_invalid_two_in_middle(self):

        index_pattern, err = validate_index_pattern("t*e*st")

        assert err == "If two wildcards are supplied, they must be at the start and end." and index_pattern == "t%e%st"

    def test_validate_index_pattern_invalid_three_in_middle(self):

        index_pattern, err = validate_index_pattern("te*s*t*")

        assert err == "Index Pattern must contain no more than two asterisk" and index_pattern == "te%s%t%"


class TestMain():

    test_user = User(
        username="testuser", id=1, password="ee", time_created="00", time_updated="00", updated_by=1, type=1)

    test_admin = User(
        username="testadmin", id=1, password="ee", time_created="00", time_updated="00", updated_by=1, type=3)

    def test_health(self):

        assert main.health() == {'app_health': True,
                                 'db_health': True, 'hostname': 'Benjamins-MBP'}

    def test_ingest_logs(self):

        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })

        assert main.ingest_log(payload, self.test_user) == {
            'fields_unpacked': 2, 'success': True}

    def test_get_logs(self):

        # Add in some logs!
        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        res = main.get_logs("testindex", self.test_user)

        for k in res:
            del k['timestamp']

        assert res == [{'field': 'time', 'index_name': 'testindex', 'message': '123124124', 'source': 'testsource'}, {
            'field': 'message', 'index_name': 'testindex', 'message': 'a test message', 'source': 'testsource'}]

    def test_get_logs_from_name(self):

        # Add in some logs!
        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        payload = request.LogPayload(index="testindex1", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        res = main.get_all_indexes(self.test_user)

        for k in res:
            del k['time_created']
            del k['time_updated']

        assert res == [{
            "name": "testindex",
            "updated_by": 1
        }, {
            "name": "testindex1",
            "updated_by": 1
        }]

    def test_get_logs_from_pattern(self):

        # Add in some logs!
        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        payload = request.LogPayload(index="testindex1", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        res = main.get_logs_from_pattern(
            request.IndexPatternPayload(index_pattern="testindex*"), self.test_user)

        for k in res:
            del k['timestamp']

        assert res == [{'index_name': 'testindex', 'field': 'time', 'message': '123124124', 'source': 'testsource'}, {'index_name': 'testindex', 'field': 'message', 'message': 'a test message', 'source': 'testsource'}, {
            'index_name': 'testindex1', 'field': 'time', 'message': '123124124', 'source': 'testsource'}, {'index_name': 'testindex1', 'field': 'message', 'message': 'a test message', 'source': 'testsource'}]

    def test_delete_index_not_authed(self):

        # Add in some logs!
        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })
        main.ingest_log(payload, self.test_user)

        assert main.delete_index(
            "testindex", self.test_user).status_code == 403

    def test_delete_index_doesnt_exist(self):

        assert main.delete_index(
            "testindex", self.test_admin).status_code == 404

    def test_delete_index(self):

        # Add in some logs!
        payload = request.LogPayload(index="testindex", source="testsource", payload={
            "time": 123124124,
            "message": "a test message"
        })

        main.ingest_log(payload, self.test_user)

        assert main.delete_index(
            "testindex", self.test_admin) == 204

    def test_create_user(self):

        assert main.create_user(request.NewUser(
            username="newuser", user_password="password", type=2), self.test_admin) == {"success": True}

    def test_create_user_already_exists(self):

        assert main.create_user(request.NewUser(
            username="testuser", user_password="password", type=2), self.test_admin).status_code == 400

    def test_create_user_not_authed(self):

        assert main.create_user(request.NewUser(
            username="testuser", user_password="password", type=2), self.test_user).status_code == 403
