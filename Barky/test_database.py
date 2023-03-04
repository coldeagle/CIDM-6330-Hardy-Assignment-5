# the database module is much more testable as its actions are largely atomic
# that said, the database module could certain be refactored to achieve decoupling
# in fact, either the implementation of the Unit of Work or just changing to sqlalchemy would be good.

import os
from datetime import datetime
import sqlite3
import pytest
from database import DatabaseManager
from models import Bookmark
table_name = 'bookmarks' # Will likey make this an env var, having things like table names hard coded makes me cringe


@pytest.fixture
def database_manager() -> DatabaseManager:
    """
    What is a fixture? https://docs.pytest.org/en/stable/fixture.html#what-fixtures-are
    """
    filename = "test_bookmarks.db"
    dbm = DatabaseManager(filename)
    # what is yield? https://www.guru99.com/python-yield-return-generator.html
    yield dbm
    dbm.__del__()           # explicitly release the database manager
    os.remove(filename)


def test_database_manager_create_and_drop_table(database_manager):
    # arrange and act
    _setup_db(database_manager)

    #assert
    conn = database_manager.connection
    cursor = conn.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type=? AND name=?", ['table', table_name])

    assert cursor.fetchone()[0] == 1

    #Testing drop (just in case)
    database_manager.drop_table(table_name)
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type=? AND name=?", ['table', table_name])
    assert cursor.fetchone()[0] == 0


def test_database_manager_add_bookmark(database_manager):

    # arrange
    _setup_db(database_manager)

    data = _default_bookmark()

    # act
    database_manager.add(table_name, data)

    # assert
    record = _do_query_from_title(database_manager, data.title)
    assert record[0] == 1


def test_database_manager_delete_bookmark(database_manager):

    # arrange
    _setup_db(database_manager)

    data = _default_bookmark()

    # act
    database_manager.add(table_name, data)

    # assert
    assert (_do_query_from_title(database_manager, data.title).fetchone()[0] == 1, "Returned record Id should be 1!")


def test_database_manager_delete_bookmark(database_manager):

    # arrange
    _setup_db(database_manager)

    data = _default_bookmark()
    database_manager.add(table_name, data)
    record = _do_query_from_title(database_manager, data.title)

    assert(record[1] == data.title, "The record returned should have matched the title name!")

    # act
    database_manager.delete(table_name, {"title": record[1]})

    # asserting that there is no longer a record
    assert (_do_query_from_title(database_manager, data.title) is None, "There should hae been nothing returned")


def test_select(database_manager):
    # arrange
    _setup_db(database_manager)
    data = _default_bookmark()

    database_manager.add(table_name, data)

    original_title = data.title+''

    data.title = data.title+'-2'

    database_manager.add(table_name, data)

    # act
    results = database_manager.select(table_name=table_name, criteria={'notes': data.notes}, order_by="id desc")

    # asserting that there were two records returned and they were sorted properly
    records = results.fetchall()
    assert(len(records), 2, "There weren't enough records returned!")
    assert(records[0][1] != original_title, "The first record returned should have been the second created!")
    assert(records[1][1] == original_title, "The last record returned should have been the first created!")


def _do_query_from_title(database_manager, title):
    conn = database_manager.connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM "+table_name+" WHERE title=?", [title])

    return cursor.fetchone()


def _do_add(database_manager):
    # act
    database_manager.add(table_name, _default_bookmark())


def _setup_db(database_manager):
    database_manager.create_table(
        table_name,
        {
            "id": "integer primary key autoincrement",
            "title": "text not null",
            "url": "text not null",
            "notes": "text",
            "date_added": "text not null",
        },
    )


def _default_bookmark():
    return Bookmark(title='test_title', url='http://example.com', notes='test notes', date_added=datetime.utcnow().isoformat())

