import inspect
import json
from collections import OrderedDict
from typing import Dict, List


def to_json(content):
    val = dict()
    val['result'] = content
    return val


def check_if_param_has_keys(params: Dict[str, str], keys: List[str]):
    if len(set(keys).difference(set(params.keys()))) == 0:
        return True
    else:
        return False


def make_log_message(message: str) -> str:
    return f"<LOG [{inspect.stack()[2][3]}]> {message}"


def make_error_message(message: str) -> str:
    return f"<ERROR [{inspect.stack()[2][3]}]> {message}"
