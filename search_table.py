from threading import Lock
from functools import lru_cache

from sqlite3 import Cursor
import config

@lru_cache
def get_unit_name(id: int, cursor: Cursor) -> str:
    config.lock.acquire(True)
    name = ""
    try:
        if id != None:
            cursor.execute(f"""SELECT Name FROM Unit WHERE ID={id}""")
            name = cursor.fetchone()
    finally:
        config.lock.release()
        if name != "":
            return name[0]
        else:
            return ""
    

@lru_cache
def get_unit_id(name: str, cursor: Cursor) -> int:
    config.lock.acquire(True)
    id = 0
    try:
        cursor.execute(f"""SELECT ID FROM Unit WHERE Name='{name}'""")
        id  = cursor.fetchone()
    finally:
        config.lock.release()
        if id == None:
            return id
        else:
            return id[0]