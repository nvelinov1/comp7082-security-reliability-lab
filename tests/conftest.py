import os.path
import sqlite3

import pytest

from checkout import CheckoutService
from payments import FakePaymentGateway
from repository import StoreRepository
from setup_db import exec_sample_queries

TEST_DB_PATH = "test.db"

@pytest.fixture(autouse=True, scope="function")
def seed_db():
    conn = sqlite3.connect(TEST_DB_PATH)
    exec_sample_queries(conn)
    conn.commit()
    yield TEST_DB_PATH
    conn.close()

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture
def get_repo(seed_db):
    return StoreRepository(seed_db)

@pytest.fixture
def get_checkout(get_repo):
    return CheckoutService(get_repo, FakePaymentGateway())

@pytest.fixture
def get_failed_checkout(get_repo):
    return CheckoutService(get_repo, FakePaymentGateway(False))
