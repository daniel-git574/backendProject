from typing import Union
from pydantic import BaseModel

class ArrayItem(BaseModel):
    # This model wraps a single "value" field.
    # Updated: Instead of 'Any', restrict it to specific allowed types.
    # This means the value can be a String OR an Integer OR a Float.
    value: Union[str, int, float]