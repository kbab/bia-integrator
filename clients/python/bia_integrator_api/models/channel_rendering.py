# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import List, Optional, Union
from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr, conlist

class ChannelRendering(BaseModel):
    """
    ChannelRendering
    """
    channel_label: Optional[StrictStr] = Field(...)
    colormap_start: conlist(Union[StrictFloat, StrictInt]) = Field(...)
    colormap_end: conlist(Union[StrictFloat, StrictInt]) = Field(...)
    scale_factor: Optional[Union[StrictFloat, StrictInt]] = 1
    __properties = ["channel_label", "colormap_start", "colormap_end", "scale_factor"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> ChannelRendering:
        """Create an instance of ChannelRendering from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # set to None if channel_label (nullable) is None
        # and __fields_set__ contains the field
        if self.channel_label is None and "channel_label" in self.__fields_set__:
            _dict['channel_label'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ChannelRendering:
        """Create an instance of ChannelRendering from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ChannelRendering.parse_obj(obj)

        _obj = ChannelRendering.parse_obj({
            "channel_label": obj.get("channel_label"),
            "colormap_start": obj.get("colormap_start"),
            "colormap_end": obj.get("colormap_end"),
            "scale_factor": obj.get("scale_factor") if obj.get("scale_factor") is not None else 1
        })
        return _obj

