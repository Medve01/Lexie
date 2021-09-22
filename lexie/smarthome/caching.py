import json
import logging
from os.path import exists
from typing import Any

from pymemcache.client import base
from pymemcache.exceptions import MemcacheError


def get_client() -> base.Client:
    """ returns  pypmemcache.base.client parametrized """
    if exists("config.json"):
        with open("config.json", encoding="UTF-8") as configfile: # pragma: nocover
            config = json.load(configfile) # pragma: nocover
    elif exists("lexie/config.json"):
        with open("lexie/config.json", encoding="UTF-8") as configfile:
            config = json.load(configfile)
    else:
        raise Exception('Cannot find configfile :/') # pragma: nocover
    client = base.Client(server=(config["MEMCACHED_HOST"], config["MEMCACHED_PORT"]))
    return client

def get_value_from_cache(key: str) -> Any:
    """ fetches a key from memcached """
    try:
        client = get_client()
        cached_value = client.get(key)
        if cached_value is None:
            return None
        return json.loads(cached_value.decode())
    except MemcacheError: #pragma: nocover
        logging.error("Exception during memcached read") #pragma: nocover
        return None #pragma: nocover

def set_value_in_cache(key: str, value: Any) -> bool:
    """ sets a cache value """
    try:
        client = get_client()
        client.set(key, json.dumps(value))
        return True
    except MemcacheError: #pragma: nocover
        logging.error("Exception during memcached read") #pragma: nocover
        return False #pragma: nocover

def flush_cache() -> None:
    """ flushes memcached. To be called on Lexie startup """
    client = get_client()
    client.flush_all()
