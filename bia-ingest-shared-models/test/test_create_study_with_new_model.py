from bia_ingest_sm.shared_models import Study
from bia_ingest_sm.biostudies import (
    Submission,
)
from bia_ingest_sm.conversion import get_study_from_submission

def test_create_study_with_new_model(test_submission):
    study = get_study_from_submission(test_submission)
    assert study is not None
