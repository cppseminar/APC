"""Wrappers for cosmos(mongo api)."""
import logging
import os

# For type hints only
import pymongo.collection  # pylint: disable=unused-import

from pymongo import MongoClient
from bson import ObjectId
from . import common
from . import users


def get_client():
    """Get Mongo instance. Try to reuse last connection."""
    try:
        client = MongoClient(
            os.environ["MyCosmosDBConnectionString"], retryWrites=False
        )
        return _Mongo(client.get_database(common.DB_NAME))
    except Exception as error:
        logging.error("Error connecting to mongo %s", error)
        raise


class _Mongo:
    def __init__(self, client):
        self.client = client

    def get_users(self) -> pymongo.collection.Collection:
        """Return users collection."""
        return self.client.get_collection(common.COL_USERS)

    def get_submissions(self) -> pymongo.collection.Collection:
        """Return submissions collection."""
        return self.client.get_collection(common.COL_SUBMISSIONS)


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

    @staticmethod
    def get_submission(submission_id: str):
        """Get submissions identified by submission_id."""
        pass


class MongoSubmissions:
    """Manipulation of submissions."""

    @staticmethod
    def get_submissions(limit=10, skip=0):
        """Get all submissions."""
        collection = get_client().get_submissions()
        cursor = collection.find({}, {"files": 0}).limit(limit).skip(skip)
        return iter(cursor)

    @staticmethod
    def get_submission(submission_id=None):
        """Get specific submission."""
        sub_id = ObjectId(submission_id)
        collection = get_client().get_submissions()
        return collection.find_one({"_id": sub_id})

    @staticmethod
    def submit(user="", files=None, task_id=""):
        """Submit one entry to submissions."""
        collection = get_client().get_submissions()
        if not files:
            files = list()
        document = {
            "user": user,
            "files": files,
            "task_id": task_id
        }
        result = collection.insert_one(document)
        if not result.acknowledged:
            return None
        document["_id"] = result.inserted_id
        return document
