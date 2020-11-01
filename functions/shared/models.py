import dataclasses
import datetime
import typing

from .core import ModelBase

from bson import ObjectId


@dataclasses.dataclass
class TestCase(ModelBase):
    task_id: ObjectId
    name: str
    runs_allowed: int
    docker: str
    roles: typing.List[str] = dataclasses.field(default_factory=list)
    does_count: bool = True

    def map_item(self, item):
        key, value = item
        mapper = {
            "does_count": "doesCount",
            "runs_allowed": "numRunsAllowed",
            "_id": "id",
        }
        return mapper.get(key, key), value

    def filter_item(self, item):
        key, _ = item
        if key in ["roles", "task_id", "docker"]:
            return False
        return True


@dataclasses.dataclass
class Submission(ModelBase):
    """Representation of submission in db."""

    user: str  # User email
    task_id: ObjectId
    date: datetime.datetime
    runs_count: int = 0
    is_final: bool = False
    files: typing.List[typing.Any] = dataclasses.field(default_factory=list)
    task_name: str = ""

    def map_item(self, item):
        key, value = item
        mapper = {
            "_id": "id",
            "runs_count": "testsRunCount",
            "is_final": "isFinal",
            "task_name": "taskName",
        }
        if key in mapper:
            return mapper[key], value
        return super().map_item(item)

    def filter_item(self, item):
        key, value = item
        if key == "files" and not value:
            return False

        filter_map = {"task_id": False}
        return filter_map.get(key, True)


@dataclasses.dataclass
class TestRun(ModelBase):
    """Representation of one test run."""
    submission_id: ObjectId
    case_id: ObjectId
    user: str
    requested: datetime.datetime
    description: str = ""
    case_name: str = ""
    task_name: str = ""


    def map_item(self, item):
        key, value = item
        mapper = {
            "_id": "id",
            "case_id": "caseId",
            "submission_id": "submissionId",
            "task_name": "taskName",
            "case_name": "caseName",
        }
        if key in mapper:
            return mapper[key], value
        return super().map_item(item)

    def filter_item(self, item):
        key, value = item
        if key == "description" and not value:
            return False
        return super().filter_item(item)


@dataclasses.dataclass
class Task(ModelBase):
    """Representation of one assignment in out system."""
    name: str
    description: str = ""
    roles: typing.List[str] = dataclasses.field(default_factory=list)
    valid_until: typing.Optional[datetime.datetime] = None

    def map_item(self, item):
        key, value = item
        mapper = {
            "_id": "id",
        }
        if key in mapper:
            return mapper[key], value
        return super().map_item(item)

    def filter_item(self, item):
        key, _ = item
        if key in ["valid_until", "roles"]:
            return False
        return super().filter_item(item)
