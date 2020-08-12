"""Functions without application logic, required in multiple modules."""
from bson import ObjectId

def schema_object_id_validator(field, value, error):
    """Cerberus object id validator."""
    if not ObjectId.is_valid(value):
        error(field, "value doesn't seem like object id")
