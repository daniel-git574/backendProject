# services/array_service.py
from fastapi import HTTPException

# In-memory array storage (simple demo state shared across requests)
array_storage: list = ["first", "second", "third"]

def get_all() -> list:
    """Return the whole array."""
    return array_storage

def get_by_index(index: int) -> dict:
    """Return a single item by index or 404 if out of range."""
    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")
    return {"value": array_storage[index]}

def add(value) -> list:
    """Append a new value to the end of the array and return the array."""
    array_storage.append(value)
    return array_storage

def update(index: int, value):
    """Replace the value at a given index or 404 if out of range."""
    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")
    array_storage[index] = value
    return {"index": index, "value": value}

def delete_last():
    """Pop the last value or 400 if the array is empty."""
    if not array_storage:
        raise HTTPException(status_code=400, detail="Array is empty")
    deleted = array_storage.pop()
    return {"deleted": deleted, "array": array_storage}

def reset_index(index: int):
    """
    Set a given index to 0 (per assignment requirement) or 404 if out of range.
    This does NOT remove the element — it overwrites it with 0.
    """
    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")
    array_storage[index] = 0
    return {"index": index, "array": array_storage}
