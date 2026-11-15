import os
from . import sqlite, mysql

if os.getenv("MYSQL_HOST") or os.getenv("MYSQL_HOST_FILE"):
    _backend = mysql
else:
    _backend = sqlite

init = _backend.init
teardown = _backend.teardown
get_items = _backend.get_items
get_item = _backend.get_item
store_item = _backend.store_item
update_item = _backend.update_item
remove_item = _backend.remove_item

__all__ = [
    "init",
    "teardown",
    "get_items",
    "get_item",
    "store_item",
    "update_item",
    "remove_item",
]
