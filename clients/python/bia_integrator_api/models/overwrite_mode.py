# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import json
import pprint
import re  # noqa: F401
from aenum import Enum, no_arg





class OverwriteMode(str, Enum):
    """
    OverwriteMode
    """

    """
    allowed enum values
    """
    FAIL = 'fail'
    ALLOW_IDEMPOTENT = 'allow_idempotent'

    @classmethod
    def from_json(cls, json_str: str) -> OverwriteMode:
        """Create an instance of OverwriteMode from a JSON string"""
        return OverwriteMode(json.loads(json_str))


