"""Wrappers for cosmos(mongo api).

All mongo logic - searching, insering, updating and is hidden right here.
Another important thing in this module is caching of mongo connection.  Every
time there is new connection request (this is actually throttled to 20
seconds), we try one simple command at first, so if connection is no longer
working, we can open new one.
"""
import datetime
import logging
import os
import time
import typing

# For type hints only
import pymongo.collection  # pylint: disable=unused-import

from pymongo import MongoClient
from bson import ObjectId
from . import common
from . import users


# These variables are global as there is a chance, they will survive
# between invocations and save us some time

_GLOBAL_MONGO = None  # Mongo connection to database (class _Mongo)
_GLOBAL_MONGO_CHECKUP = None  # Last successfull action as timestamp


def __get_new_conn():
    client = MongoClient(os.environ["MyCosmosDBConnectionString"], retryWrites=False)
    return _Mongo(client.get_database(common.DB_NAME))


def __mark_success():
    global _GLOBAL_MONGO_CHECKUP
    _GLOBAL_MONGO_CHECKUP = time.time()


def get_client():
    """Return instance of _Mongo with set up connection.

    If connection exists and is new, reuse it. If it is old, check if it is
    working and reuse it, or create new one.
    """
    global _GLOBAL_MONGO_CHECKUP
    global _GLOBAL_MONGO
    last_success = _GLOBAL_MONGO_CHECKUP or 1
    if last_success + 20 < time.time():  # 20 seconds max age
        # We must recheck connection, it is too old now
        try:
            # _GLOBAL_MONGO might be None, but we will catch this anyway
            _GLOBAL_MONGO.get_users().find_one({}, {"_id": 1})
            __mark_success()
            return _GLOBAL_MONGO
        except AttributeError:
            # This error means that mongo was None - it is init - don't log
            pass
        except:  # We don't know, what mongo may throw so ...
            # We are interested in this log message, so we know, how servers
            # generally behave
            logging.warning("Creating new connection to mongo.")
            logging.warning("WARNING: This should not happen often!")
    else:  # Connection is fresh
        return _GLOBAL_MONGO
    # We must create new connection, old one is closed or doesn't exist
    _GLOBAL_MONGO = __get_new_conn()
    __mark_success()
    return _GLOBAL_MONGO


class _Mongo:
    def __init__(self, client):
        self.client = client

    def get_users(self) -> pymongo.collection.Collection:
        """Return users collection."""
        return self.client.get_collection(common.COL_USERS)

    def get_submissions(self) -> pymongo.collection.Collection:
        """Return submissions collection."""
        return self.client.get_collection(common.COL_SUBMISSIONS)

    def get_tasks(self) -> pymongo.collection.Collection:
        """Return tasks collection."""
        return self.client.get_collection(common.COL_TASKS)


class MongoUsers:
    """Collection of methods for working with users collection."""

    @staticmethod
    def get_user(email: str):
        """Get or create user defined by email."""
        collection = get_client().get_users()
        entry = collection.find_one({common.SCHEMA_USER.EMAIL: email}) or {}
        if not entry:
            # Solve race condition during new user creation by upsert
            collection.update_one(
                {common.SCHEMA_USER.EMAIL: email},
                {
                    "$setOnInsert": {
                        common.SCHEMA_USER.EMAIL: email,
                        common.SCHEMA_USER.ROLES: [],
                        common.SCHEMA_USER.IS_ADMIN: False,
                    }
                },
                upsert=True,
            )
        is_admin = bool(entry.get(common.SCHEMA_USER.IS_ADMIN, False))
        roles = list(entry.get(common.SCHEMA_USER.ROLES, []))
        return users.User(email=email, is_admin=is_admin, roles=roles)


class MongoSubmissions:
    """Manipulation of submissions."""

    @staticmethod
    def get_submissions(limit=10, skip=0, user=None):
        """Get all submissions."""
        collection = get_client().get_submissions()
        query = {}
        if user:
            query["user"] = user
        cursor = (
            collection.find(query, {"files": 0})
            .limit(limit)
            .skip(skip)
            .sort([("date", pymongo.DESCENDING)])
        )
        return iter(cursor)

    @staticmethod
    def get_submission(submission_id=None):
        """Get specific submission."""
        sub_id = ObjectId(submission_id)
        collection = get_client().get_submissions()
        return collection.find_one({"_id": sub_id})

    @staticmethod
    def submit(user="", files=None, task_id="", date=None):
        """Submit one entry to submissions."""
        collection = get_client().get_submissions()
        if not files:
            files = list()
        if not date:
            date = datetime.datetime.now(datetime.timezone.utc)
        document = {
            "user": user,
            "files": files,
            "task_id": task_id,
            "date": date,
            "isFinal": False,
            "testsRunCount": 0,
            "tests" : []
        }
        result = collection.insert_one(document)
        if not result.acknowledged:
            return None
        document["_id"] = result.inserted_id
        return document


class MongoTasks:
    @staticmethod
    def get_task(task_id, roles: typing.List = None):
        query = {"_id": task_id}
        if roles != None:
            # This user is not an admin, so we must select only those tasks,
            # with correct roles assigned
            query["roles"] = {"$in": roles}

        collection = get_client().get_tasks()
        return collection.find_one(query)

    @staticmethod
    def get_tasks(roles: typing.List = None):
        query = {}
        if roles != None:
            # This user is not an admin, so we must select only those tasks,
            # with correct roles assigned
            query["roles"] = {"$in": roles}

        collection = get_client().get_tasks()
        return collection.find(query, {"name": 1})

