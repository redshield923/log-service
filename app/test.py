# test.py

from ctypes import create_string_buffer
from distutils.dep_util import newer_pairwise
from hashlib import new
import sqlite3
from models.database import User
from helpers.database import DatabaseHelper
from helpers.log import LogHelper
from helpers.user import UserHelper
from config.config import Config
from helpers.auth import AuthHelper
from utils import validate_index_pattern
import pytest
from fastapi import FastAPI, Depends, HTTPException, status


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
        assert authHelper.correct_password(password_hash, 'password') == True

    def test_correct_password_invalid(self):
        # SHA256 hash of 'password'
        password_hash = 'ww'
        assert authHelper.correct_password(password_hash, 'password') == False

    # Auth::authenticate_user.

    def test_authenticate_user_correct_details(self):

        user = authHelper.authenticate_user('testuser', 'password')

        assert user.username == 'testuser'

    def test_authenticate_user_wrong_password(self):

        user = authHelper.authenticate_user('testuser', 'password1')

        assert user == False

    def test_authenticate_user_wrong_username(self):

        user = authHelper.authenticate_user('testuser2', 'password')

        assert user == False

    # Auth::get_user

    def test_get_user_valid(self):

        user = authHelper.get_user('testuser')

        assert user.username == 'testuser'

    def test_get_user_invalid(self):

        user = authHelper.get_user('no')

        assert user == None


class TestUser:

    # User::create_new_user

    def test_create_new_user_valid(self):

        # Insert new user with method to test

        userHelper.create_new_users('newuser', 'passwordhash', 1, 1)

        # Grab our newly created user
        user = authHelper.get_user('newuser')

        assert user.username == 'newuser'

    def test_create_new_user_invalid_params(self):

        # Insert new user with method to test

        assert userHelper.create_new_users(
            'newuser', 'passwordhash', 7, 7) == False

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
        userHelper.create_new_users('newuser', 'passwordhash', 1, 1)

        userHelper.delete_user('newuser')

        assert authHelper.get_user('newuser') == None


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

    def test_create_index_valid(self):

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
        assert logHelper.retrieve_index('testindex') == False

    # Log::create_if_not_exists

    def test_index_if_exists_does(self):
        logHelper.create_index('testindex', 1)

        assert logHelper.create_if_not_exists('testindex', 1) == False

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

        assert logHelper.retrieve_index('testindex') == False


class TestUtils:

    # Utils::validate_index_pattern

    def test_validate_index_pattern_good_end(self):

        index_pattern, err = validate_index_pattern("test*")

        assert err == None and index_pattern == "test%"

    def test_validate_index_pattern_good_start(self):

        index_pattern, err = validate_index_pattern("*test")

        assert err == None and index_pattern == "%test"

    def test_validate_index_pattern_good_start(self):

        index_pattern, err = validate_index_pattern("*test*")

        assert err == None and index_pattern == "%test%"

    def test_validate_index_pattern_invalid_no_asteriks(self):

        index_pattern, err = validate_index_pattern("test")

        assert err == "Index Pattern must contain asterisk"

    def test_validate_index_pattern_invalid_in_middle(self):

        index_pattern, err = validate_index_pattern("te*st")

        assert err == "Wildcards must be at the start and end."

    def test_validate_index_pattern_invalid_in_middle(self):

        index_pattern, err = validate_index_pattern("t*e*st")

        assert err == "If two wildcards are supplied, they must be at the start and end."

    def test_validate_index_pattern_invalid_in_middle(self):

        index_pattern, err = validate_index_pattern("te*s*t*")

        assert err == "Index Pattern must contain no more than two asterisk"
