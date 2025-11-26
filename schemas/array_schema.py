from typing import Any
from pydantic import BaseModel

class ArrayItem(BaseModel):
    # This model wraps a single "value" field that can be any JSON-serializable type.
    # Used by POST /array and PUT /array/{index}.
    value: Any


