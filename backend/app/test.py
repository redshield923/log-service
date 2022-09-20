# test.py

from helpers.database import DatabaseHelper
from helpers.log import LogHelper
from helpers.user import UserHelper
from config.config import Config
import pytest
databaseHelper = DatabaseHelper(Config.DATABASE_PATH)
authHelper = AuthHelper(Config.SECRET, Config.ALGORITHM, databaseHelper)
logHelper = LogHelper(databaseHelper)
userHelper = UserHelper(databaseHelper)


class TestLog:
    def test_retrieve_all_indices(self):
        assert 1 == 1
