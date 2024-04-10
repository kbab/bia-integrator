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


from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr, conlist, constr
from bia_integrator_api.models.author import Author
from bia_integrator_api.models.model_metadata import ModelMetadata
from bia_integrator_api.models.study_annotation import StudyAnnotation

class BIAStudy(BaseModel):
    """
    BIAStudy
    """
    attributes: Optional[Dict[str, Any]] = Field(None, description="         When annotations are applied, the ones that have a key different than an object attribute (so they don't overwrite it) get saved here.     ")
    annotations_applied: Optional[StrictBool] = Field(False, description="         This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn't.     ")
    annotations: Optional[conlist(StudyAnnotation)] = None
    context: Optional[constr(strict=True, min_length=1)] = Field('https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/StudyContext.jsonld', alias="@context")
    uuid: StrictStr = Field(...)
    version: StrictInt = Field(...)
    model: Optional[ModelMetadata] = None
    title: StrictStr = Field(...)
    description: StrictStr = Field(...)
    authors: Optional[conlist(Author)] = None
    organism: StrictStr = Field(...)
    release_date: StrictStr = Field(...)
    accession_id: StrictStr = Field(...)
    imaging_type: Optional[StrictStr] = None
    example_image_uri: Optional[StrictStr] = ''
    example_image_annotation_uri: Optional[StrictStr] = ''
    tags: Optional[conlist(StrictStr)] = None
    file_references_count: Optional[StrictInt] = 0
    images_count: Optional[StrictInt] = 0
    __properties = ["attributes", "annotations_applied", "annotations", "@context", "uuid", "version", "model", "title", "description", "authors", "organism", "release_date", "accession_id", "imaging_type", "example_image_uri", "example_image_annotation_uri", "tags", "file_references_count", "images_count"]

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
    def from_json(cls, json_str: str) -> BIAStudy:
        """Create an instance of BIAStudy from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in annotations (list)
        _items = []
        if self.annotations:
            for _item in self.annotations:
                if _item:
                    _items.append(_item.to_dict())
            _dict['annotations'] = _items
        # override the default output from pydantic by calling `to_dict()` of model
        if self.model:
            _dict['model'] = self.model.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in authors (list)
        _items = []
        if self.authors:
            for _item in self.authors:
                if _item:
                    _items.append(_item.to_dict())
            _dict['authors'] = _items
        # set to None if model (nullable) is None
        # and __fields_set__ contains the field
        if self.model is None and "model" in self.__fields_set__:
            _dict['model'] = None

        # set to None if authors (nullable) is None
        # and __fields_set__ contains the field
        if self.authors is None and "authors" in self.__fields_set__:
            _dict['authors'] = None

        # set to None if imaging_type (nullable) is None
        # and __fields_set__ contains the field
        if self.imaging_type is None and "imaging_type" in self.__fields_set__:
            _dict['imaging_type'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> BIAStudy:
        """Create an instance of BIAStudy from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return BIAStudy.parse_obj(obj)

        _obj = BIAStudy.parse_obj({
            "attributes": obj.get("attributes"),
            "annotations_applied": obj.get("annotations_applied") if obj.get("annotations_applied") is not None else False,
            "annotations": [StudyAnnotation.from_dict(_item) for _item in obj.get("annotations")] if obj.get("annotations") is not None else None,
            "context": obj.get("@context") if obj.get("@context") is not None else 'https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/StudyContext.jsonld',
            "uuid": obj.get("uuid"),
            "version": obj.get("version"),
            "model": ModelMetadata.from_dict(obj.get("model")) if obj.get("model") is not None else None,
            "title": obj.get("title"),
            "description": obj.get("description"),
            "authors": [Author.from_dict(_item) for _item in obj.get("authors")] if obj.get("authors") is not None else None,
            "organism": obj.get("organism"),
            "release_date": obj.get("release_date"),
            "accession_id": obj.get("accession_id"),
            "imaging_type": obj.get("imaging_type"),
            "example_image_uri": obj.get("example_image_uri") if obj.get("example_image_uri") is not None else '',
            "example_image_annotation_uri": obj.get("example_image_annotation_uri") if obj.get("example_image_annotation_uri") is not None else '',
            "tags": obj.get("tags"),
            "file_references_count": obj.get("file_references_count") if obj.get("file_references_count") is not None else 0,
            "images_count": obj.get("images_count") if obj.get("images_count") is not None else 0
        })
        return _obj


