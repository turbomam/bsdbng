import pytest
from pydantic import ValidationError

from bsdbng.datamodel import Study


def test_study_record_requires_source_record_id() -> None:
    with pytest.raises(ValidationError, match="source_record_id"):
        Study.model_validate({"id": "bsdb:12345", "experiments": []})
