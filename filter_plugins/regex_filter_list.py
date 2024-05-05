# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# pylint: disable=missing-class-docstring

# Copyright: (c) 2024, Frank Hofmann <fh@itup.dev>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['stable'],
    'version': '05.05.2024'}

DOCUMENTATION = """
module: regex_filter_list
short_description: Regex filter key/values
description:
  - Filter key/value pairs with regex search from a list with dictionaries.
  - The filter criteria(s) are stored in a list
  - Optional it is possible to negate match
  - The idea was inspired for a simpler way to filter complex json results
"""

EXAMPLES = """
- set_fact:
    filter: ["han.*"]
    data_list: 
      - {"name": "hans", "other": "value 1"}
      - {"name": "haro", "other": "value 2"}
      - {"name": "franz", "other": "value 3"}

- name: Filter by name
  debug: msg="{{ data_list | regex_filter_list('name', filter, False)}}"

- name: Negate filter by name
  debug: msg="{{ data_list | regex_filter_list('name', filter, True)}}"
"""

RETURN = """
TASK [Filter by name] *****
ok: [localhost] => {
    "msg": [{"name": "hans","other": "value 1"}]
}

TASK [Negate filter by name] ******
ok: [localhost] => {
    "msg": [
        {"name": "haro","other": "value 2"},
        {"name": "franz","other": "value 3"}
    ]
}
"""

import re
from typing import Union


class FilterModule(object):
    def filters(self):
        """ansible filter import"""
        return {
            'regex_filter_list': self.regex_filter_list
        }

    @staticmethod
    def regex_filter_list(value, key_name, filter_list, negate=False):
        """filter key/value pairs from a list or dict"""
        return filter_key_value(value, key_name, filter_list, negate)


def filter_key_value(mylist, filter_key_name, filter_list, negate=False) -> Union[dict, list, None]:
    """
    filter key/value pairs from a list or dict.
    the value must regex_match a string from a list (filter_list).
    :param mylist: list or dict (cant filter nested keys) to iterate
    :param filter_key_name: the key_name for filter values
    :param filter_list: list with string to match the value of key_name
    :param negate: you can negate the regex_search result.
    :return: result a filtered list of dict(s)
    """
    filtered_list = []
    if isinstance(mylist, list):
        for entry in mylist:
            verify_dict = filter_key_value(entry, filter_key_name, filter_list, negate)
            if verify_dict or verify_dict is None:
                filtered_list.append(entry)

    if isinstance(mylist, dict):
        for key, value in mylist.items():
            if key == filter_key_name:
                if regex_from_list(value, filter_list, negate):
                    return {key: value}
                return {}
        return None
    return filtered_list


def regex_from_list(value, expr_list, negate=False) -> bool:
    """
    filter regex from list
    :param value: string that must match the expr_list
    :param expr_list: match list with strings
    :param negate: negate match from re.search
    :return: bool that match or not match the expr_list string(s)
    """
    match_list = False
    expr_list = [expr_list] if not isinstance(expr_list, list) else expr_list
    for expr in expr_list:
        if re.search(expr, value) and not match_list:
            match_list = True
        if not match_list:
            match_list = False
    if negate:
        match_list = not bool(match_list)
    return match_list
