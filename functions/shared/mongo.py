"""Wrappers for cosmos(mongo api).

All mongo logic - searching, insering and updating is hidden right here.
Another important thing in this module is caching of a mongo connection.  Every
time there is new connection request (this is actually throttled to 20
seconds), we try one simple command at first, so if connection is no longer
working, we can open new one.  This is done to prevent failure in real requests.
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
from . import common, users, models, core


# These variables are global as there is a chance, they will survive
# between invocations and save us some time

_GLOBAL_MONGO = None  # Mongo connection to database (class _Mongo)
_GLOBAL_MONGO_CHECKUP = None  # Last successfull action as timestamp


def __get_new_conn():
    client = MongoClient(os.environ[common.ENV_CONNECTION_STRING], retryWrites=False)
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

    def get_test_cases(self) -> pymongo.collection.Collection:
        """Return test cases collection."""
        return self.client.get_collection(common.COL_CASES)

    def get_tests(self) -> pymongo.collection.Collection:
        """Return collection with test results."""
        return self.client.get_collection(common.COL_TESTS)


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
    def _to_model(obj):
        """Convert mongo bson to submission model."""
        kwargs = core.empty_dataclass_dict(models.Submission)
        kwargs.update(obj)
        kwargs["task_id"] = obj["taskId"]
        kwargs["is_final"] = obj["isFinal"]
        kwargs["runs_count"] = obj["testsRunCount"]
        kwargs["task_name"] = obj.get("taskName", "")

        return core.instantiate_dataclass(models.Submission, **kwargs)

    @staticmethod
    def get_submissions(limit=10, skip=0, user=None, task_id=None):
        """Get all submissions."""
        collection = get_client().get_submissions()
        query = {}
        if user:
            query["user"] = user
        if task_id:
            query["taskId"] = task_id
        cursor = (
            collection.find(query, {"files": 0})
            .limit(limit)
            .skip(skip)
            .sort([("date", pymongo.DESCENDING)])
        )
        return core.mongo_filter_errors(cursor, MongoSubmissions._to_model)

    @staticmethod
    def get_submission(submission_id=None, user=None, full=True):
        """Get specific submission."""
        query = {"_id": submission_id}
        projection = None
        if not full:
            projection = {"files": 0}
        if user:
            query["user"] = user

        collection = get_client().get_submissions()
        return core.mongo_filter_errors(
            collection.find_one(query, projection), MongoSubmissions._to_model
        )

    @staticmethod
    def increment_test(submission_id):
        """Increment number of test runs on submission."""
        query = {"_id": submission_id}
        operation = {"$inc": {"testsRunCount": 1}}
        collection = get_client().get_submissions()
        result = collection.update_one(query, operation)
        return result.modified_count == 1


    @staticmethod
    def submit(user="", files=None, task_id="", date=None, name=""):
        """Submit one entry to submissions."""
        collection = get_client().get_submissions()
        if not files:
            files = list()
        if not date:
            date = datetime.datetime.now(datetime.timezone.utc)
        document = {
            "user": user,
            "files": files,
            "taskId": task_id,
            "date": date,
            "taskName": name,
            "isFinal": False,
            "testsRunCount": 0,
            "type": "submission",
            "tests": [],
        }
        result = collection.insert_one(document)
        if not result.acknowledged:
            return None
        document["_id"] = result.inserted_id
        return core.mongo_filter_errors(document, MongoSubmissions._to_model)


class MongoTasks:
    """Manipulation with tasks in db."""

    @staticmethod
    def get_task(task_id, roles: typing.List = None):
        """Get task with task_id, if has roles."""
        query = {"_id": task_id}
        if roles is not None:
            # This user is not an admin, so we must select only those tasks,
            # with correct roles assigned
            query["roles"] = {"$in": roles}

        collection = get_client().get_tasks()
        return collection.find_one(query)

    @staticmethod
    def get_tasks(roles: typing.List = None):
        """Get all tasks matchin roles."""
        query = {}
        if roles is not None:
            # This user is not an admin, so we must select only those tasks,
            # with correct roles assigned
            query["roles"] = {"$in": roles}

        collection = get_client().get_tasks()
        return collection.find(query, {"name": 1})


class MongoTestCases:
    """Functions for retrieving test cases from mongo."""

    @staticmethod
    def _to_model(obj):
        """Convert names between JS and python notation."""
        result = core.empty_dataclass_dict(models.TestCase)
        result.update(obj)
        result["task_id"] = result.get("taskId", "")
        result["runs_allowed"] = result["numRunsAllowed"]
        result["does_count"] = result["doesCount"]
        return core.instantiate_dataclass(models.TestCase, **result)

    @staticmethod
    def get_case(case_id: ObjectId, roles: typing.List = None) -> models.TestCase:
        """Retrieve concrete case."""
        query = {"_id": case_id}
        if roles is not None:
            query["roles"] = {"$in": roles}

        collection = get_client().get_test_cases()
        return core.mongo_filter_errors(
            collection.find_one(query), MongoTestCases._to_model
        )

    @staticmethod
    def get_cases(
        task_id: ObjectId = None, roles: typing.List = None
    ) -> typing.List[models.TestCase]:
        """Retrieve all test cases."""
        query = {}
        if task_id is not None:
            query["taskId"] = task_id
        if roles is not None:
            query["roles"] = {"$in": roles}
        collection = get_client().get_test_cases()
        result = collection.find(query)
        return core.mongo_filter_errors(result, MongoTestCases._to_model)


class MongoTests:
    """Retrieve executed/executing tests."""

    @staticmethod
    def _to_model(obj):
        """Convert dict (bson) to model."""
        kwargs = core.empty_dataclass_dict(models.TestRun)
        kwargs.update(obj)
        kwargs["case_id"] = obj["caseId"] # Necessary
        kwargs["submission_id"] = obj["submissionId"] # Necessary
        return core.instantiate_dataclass(models.TestRun, **kwargs)

    @staticmethod
    def create_test(user=None, submission_id=None, case_id=None):
        collection = get_client().get_tests()
        document = {
            "user": user,
            "submissionId": submission_id,
            "caseId": case_id,
            "requested": datetime.datetime.now(datetime.timezone.utc),
            "description": "Test run is not finished. Check back later."
        }
        result = collection.insert_one(document)

        if not result.acknowledged:
            logging.warning("Test run creation failed. Result not acknowledged")
            return None
        document["_id"] = result.inserted_id
        return core.mongo_filter_errors(document, MongoTests._to_model)

    @staticmethod
    def count_tests(case_id, user=None):
        """Count number of test runs with case_id. If user is set, count only
        test runs by that user.
        """
        collection = get_client().get_tests()
        query = {"caseId": case_id}
        if user:
            query["user"] = user
        return collection.count_documents(query)
