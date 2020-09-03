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
        if key in ["roles", "task_id"]:
            return False
        return True

@dataclasses.dataclass
class Submission(ModelBase):
    """Representation of submission in db."""
    user: str  # User email
    files: typing.Optional[typing.List[typing.Any]] = None


    def map_item(self, item):
        key, value = item
        mapper = {"_id": "id"}
        if key in mapper:
            return mapper[key], value
        return super().map_item(item)

@dataclasses.dataclass
class TestRun(ModelBase):
    """Representation of one test run."""
    submission_id: ObjectId
    case_id: ObjectId
    requested: datetime.datetime
    description: str = ""
