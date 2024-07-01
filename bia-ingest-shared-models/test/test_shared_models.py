from typing import Dict
import pytest
from . import utils
from .utils import bia_data_model, semantic_models
from bia_ingest_sm import conversion

@pytest.mark.parametrize(
    ("expected_model_func", "model_creation_func",),
    (
        (utils.get_test_affiliation, conversion.get_affiliation,),
        (utils.get_test_contributor, conversion.get_contributor,),
        (utils.get_test_publication, conversion.get_publication,),
        #(bia_data_model.Study, conversion.get_study_from_submission,),
    ),
)
def test_create_models(expected_model_func, model_creation_func, test_submission):
    expected = expected_model_func()
    created = model_creation_func(test_submission)
    assert expected == created
