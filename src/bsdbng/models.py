"""Pydantic-side development models used before LinkML codegen is introduced."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Direction = Literal["increased", "decreased"]
TaxonomicRank = Literal[
    "strain",
    "species",
    "subspecies",
    "isolate",
    "genus",
    "family",
    "order",
    "class",
    "phylum",
    "superkingdom",
]


class TaxonRecordModel(BaseModel):
    """Development-time taxon model mirroring the LinkML contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    taxon_id: str = Field(pattern=r"^NCBITaxon:[0-9]+$")
    taxon_name: str
    taxonomic_rank: TaxonomicRank


class SignatureRecordModel(BaseModel):
    """Development-time signature model mirroring the LinkML contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    signature_id: str
    direction: Direction
    taxa: tuple[TaxonRecordModel, ...]


class ExperimentRecordModel(BaseModel):
    """Development-time experiment model mirroring the LinkML contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    experiment_id: str
    experiment_name: str | None = None
    group_0_name: str | None = None
    group_1_name: str | None = None
    signatures: tuple[SignatureRecordModel, ...]


class StudyRecordModel(BaseModel):
    """Development-time study model mirroring the LinkML contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    study_id: str
    source_record_id: str
    title: str | None = None
    publication_year: int | None = None
    doi: str | None = Field(default=None, pattern=r"^10\..+$")
    experiments: tuple[ExperimentRecordModel, ...]
