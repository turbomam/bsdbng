from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.7.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'bsdbng',
     'default_range': 'string',
     'description': 'LinkML schema for normalized BugSigDB studies, experiments, '
                    'signatures, and taxa.',
     'id': 'https://w3id.org/bsdbng/schema',
     'imports': ['linkml:types'],
     'license': 'MIT',
     'name': 'bsdbng',
     'prefixes': {'NCBITaxon': {'prefix_prefix': 'NCBITaxon',
                                'prefix_reference': 'http://purl.obolibrary.org/obo/NCBITaxon_'},
                  'bsdbng': {'prefix_prefix': 'bsdbng',
                             'prefix_reference': 'https://w3id.org/bsdbng/'},
                  'bugsigdb': {'prefix_prefix': 'bugsigdb',
                               'prefix_reference': 'https://bugsigdb.org/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'schema/bsdbng.yaml',
     'title': 'BugSigDB Normalized Graph Schema'} )

class DirectionEnum(str, Enum):
    """
    Allowed values for reported abundance direction.
    """
    increased = "increased"
    decreased = "decreased"


class TaxonomicRankEnum(str, Enum):
    """
    Allowed taxonomic rank values for normalized BugSigDB taxa.
    """
    strain = "strain"
    species = "species"
    subspecies = "subspecies"
    isolate = "isolate"
    genus = "genus"
    family = "family"
    order = "order"
    class_ = "class"
    phylum = "phylum"
    superkingdom = "superkingdom"



class BugSigDBDataset(ConfiguredBaseModel):
    """
    Collection of normalized BugSigDB study records.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'title': 'Dataset',
         'tree_root': True})

    studies: list[StudyRecord] = Field(default=..., title="Study records", description="""Normalized study records in the dataset.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BugSigDBDataset']} })


class StudyRecord(ConfiguredBaseModel):
    """
    One published microbiome study from which BugSigDB collects and standardizes microbial signatures.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'study_id': {'identifier': True,
                                     'name': 'study_id',
                                     'required': True}},
         'title': 'Study'})

    study_id: str = Field(default=..., title="Study ID", description="""BugSigDB study identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    source_record_id: str = Field(default=..., title="Source Record ID", description="""Study identifier exactly as exported by BugSigDB.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    title: Optional[str] = Field(default=None, title="Title", description="""Study title.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    publication_year: Optional[int] = Field(default=None, title="Publication Year", description="""Publication year.""", ge=1900, le=2100, json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    doi: Optional[str] = Field(default=None, title="DOI", description="""Digital object identifier for the study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    experiments: list[ExperimentRecord] = Field(default=..., title="Experiments", description="""Semantic experiment units recorded for the study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })

    @field_validator('study_id')
    def pattern_study_id(cls, v):
        pattern=re.compile(r"^.+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid study_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid study_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('doi')
    def pattern_doi(cls, v):
        pattern=re.compile(r"^10\..+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid doi format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid doi format: {v}"
            raise ValueError(err_msg)
        return v


class ExperimentRecord(ConfiguredBaseModel):
    """
    One semantic unit within a study that records contrasted sample groups and key metadata relevant to differential abundance findings.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'experiment_id': {'identifier': True,
                                          'name': 'experiment_id',
                                          'required': True}},
         'title': 'Experiment'})

    experiment_id: str = Field(default=..., title="Experiment ID", description="""Experiment identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    experiment_name: Optional[str] = Field(default=None, title="Experiment Name", description="""Label for the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    group_0_name: Optional[str] = Field(default=None, title="Group 0 Name", description="""Label for one of the contrasted sample groups.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    group_1_name: Optional[str] = Field(default=None, title="Group 1 Name", description="""Label for the other contrasted sample group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    signatures: list[SignatureRecord] = Field(default=..., title="Signatures", description="""Signatures associated with the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })

    @field_validator('experiment_id')
    def pattern_experiment_id(cls, v):
        pattern=re.compile(r"^.+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid experiment_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid experiment_id format: {v}"
            raise ValueError(err_msg)
        return v


class SignatureRecord(ConfiguredBaseModel):
    """
    A microbial signature represented as an unordered set of taxa sharing a common property or response to a study condition.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'direction': {'name': 'direction', 'required': True},
                        'signature_id': {'identifier': True,
                                         'name': 'signature_id',
                                         'required': True}},
         'title': 'Signature'})

    signature_id: str = Field(default=..., title="Signature ID", description="""Signature identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SignatureRecord']} })
    direction: DirectionEnum = Field(default=..., title="Direction", description="""Reported direction of abundance change for taxa in the signature.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SignatureRecord']} })
    taxa: list[TaxonRecord] = Field(default=..., title="Taxa", description="""Taxa listed in the signature.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SignatureRecord']} })

    @field_validator('signature_id')
    def pattern_signature_id(cls, v):
        pattern=re.compile(r"^.+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid signature_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid signature_id format: {v}"
            raise ValueError(err_msg)
        return v


class TaxonRecord(ConfiguredBaseModel):
    """
    A taxonomic unit of any rank designating a microbial organism or group of microbial organisms.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'taxon_id': {'name': 'taxon_id', 'required': True},
                        'taxon_name': {'name': 'taxon_name', 'required': True},
                        'taxonomic_rank': {'name': 'taxonomic_rank', 'required': True}},
         'title': 'Taxon'})

    taxon_id: str = Field(default=..., title="Taxon ID", description="""NCBITaxon CURIE for the reported taxon.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TaxonRecord']} })
    taxon_name: str = Field(default=..., title="Taxon Name", description="""Reported taxon label.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TaxonRecord']} })
    taxonomic_rank: TaxonomicRankEnum = Field(default=..., title="Taxonomic Rank", description="""Taxonomic rank of the reported taxon.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TaxonRecord']} })

    @field_validator('taxon_id')
    def pattern_taxon_id(cls, v):
        pattern=re.compile(r"^NCBITaxon:[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid taxon_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid taxon_id format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
BugSigDBDataset.model_rebuild()
StudyRecord.model_rebuild()
ExperimentRecord.model_rebuild()
SignatureRecord.model_rebuild()
TaxonRecord.model_rebuild()
