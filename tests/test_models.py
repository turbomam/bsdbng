import pytest
from pydantic import ValidationError

from bsdbng.models import StudyRecordModel


def test_study_record_requires_source_record_id() -> None:
    with pytest.raises(ValidationError, match="source_record_id"):
        StudyRecordModel.model_validate({"study_id": "12345", "experiments": []})
