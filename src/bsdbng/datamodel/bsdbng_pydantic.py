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



class NamedThing(ConfiguredBaseModel):
    """
    An entity with a stable identifier. All identifiable classes in this schema inherit from NamedThing.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://w3id.org/bsdbng/schema',
         'title': 'Named Thing'})

    id: str = Field(default=..., title="ID", description="""Stable identifier for this entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing']} })


class BugSigDBDataset(ConfiguredBaseModel):
    """
    Collection of normalized BugSigDB study records.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'title': 'Dataset',
         'tree_root': True})

    studies: list[StudyRecord] = Field(default=..., title="Study records", description="""Normalized study records in the dataset.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BugSigDBDataset']} })


class StudyRecord(NamedThing):
    """
    One published microbiome study from which BugSigDB collects and standardizes microbial signatures.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'id': {'description': 'BugSigDB study identifier, e.g. '
                                              'bsdb:10202341.',
                               'name': 'id',
                               'pattern': '^bsdb:[0-9]+$'}},
         'title': 'Study'})

    source_record_id: str = Field(default=..., title="Source Record ID", description="""Study identifier exactly as exported by BugSigDB.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    pmid: Optional[int] = Field(default=None, title="PMID", description="""PubMed identifier for the study.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    title: Optional[str] = Field(default=None, title="Title", description="""Study title.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    publication_year: Optional[int] = Field(default=None, title="Publication Year", description="""Publication year.""", ge=1900, le=2100, json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    doi: Optional[str] = Field(default=None, title="DOI", description="""Digital object identifier for the study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    url: Optional[str] = Field(default=None, title="URL", description="""Stable URL for the study when no DOI or PMID is available.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    experiments: list[ExperimentRecord] = Field(default=..., title="Experiments", description="""Semantic experiment units recorded for the study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StudyRecord']} })
    id: str = Field(default=..., title="ID", description="""BugSigDB study identifier, e.g. bsdb:10202341.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing']} })

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

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^bsdb:[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class ExperimentRecord(NamedThing):
    """
    One semantic unit within a study that records contrasted sample groups and key metadata relevant to differential abundance findings.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'id': {'description': 'BugSigDB experiment identifier, e.g. '
                                              'bsdb:10202341/1.',
                               'name': 'id',
                               'pattern': '^bsdb:[0-9]+/[0-9]+$'}},
         'title': 'Experiment'})

    experiment_name: Optional[str] = Field(default=None, title="Experiment Name", description="""Label for the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    group_0_name: Optional[str] = Field(default=None, title="Group 0 Name", description="""Label for one of the contrasted sample groups.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    group_1_name: Optional[str] = Field(default=None, title="Group 1 Name", description="""Label for the other contrasted sample group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    signatures: list[SignatureRecord] = Field(default=..., title="Signatures", description="""Signatures associated with the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExperimentRecord']} })
    id: str = Field(default=..., title="ID", description="""BugSigDB experiment identifier, e.g. bsdb:10202341/1.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^bsdb:[0-9]+/[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class SignatureRecord(NamedThing):
    """
    A microbial signature represented as an unordered set of taxa sharing a common property or response to a study condition.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'direction': {'name': 'direction', 'required': True},
                        'id': {'description': 'BugSigDB signature identifier, e.g. '
                                              'bsdb:10202341/1/1.',
                               'name': 'id',
                               'pattern': '^bsdb:[0-9]+/[0-9]+/[0-9]+$'}},
         'title': 'Signature'})

    direction: DirectionEnum = Field(default=..., title="Direction", description="""Reported direction of abundance change for taxa in the signature.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SignatureRecord']} })
    taxa: list[TaxonRecord] = Field(default=..., title="Taxa", description="""Taxa listed in the signature.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SignatureRecord']} })
    id: str = Field(default=..., title="ID", description="""BugSigDB signature identifier, e.g. bsdb:10202341/1/1.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^bsdb:[0-9]+/[0-9]+/[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


class TaxonRecord(NamedThing):
    """
    A taxonomic unit of any rank designating a microbial organism or group of microbial organisms.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/bsdbng/schema',
         'slot_usage': {'id': {'description': 'NCBITaxon CURIE, e.g. NCBITaxon:9606.',
                               'name': 'id',
                               'pattern': '^NCBITaxon:[0-9]+$'},
                        'taxon_name': {'name': 'taxon_name', 'required': True},
                        'taxonomic_rank': {'name': 'taxonomic_rank', 'required': True}},
         'title': 'Taxon'})

    taxon_name: str = Field(default=..., title="Taxon Name", description="""Reported taxon label.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TaxonRecord']} })
    taxonomic_rank: TaxonomicRankEnum = Field(default=..., title="Taxonomic Rank", description="""Taxonomic rank of the reported taxon.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TaxonRecord']} })
    id: str = Field(default=..., title="ID", description="""NCBITaxon CURIE, e.g. NCBITaxon:9606.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NamedThing']} })

    @field_validator('id')
    def pattern_id(cls, v):
        pattern=re.compile(r"^NCBITaxon:[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid id format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
NamedThing.model_rebuild()
BugSigDBDataset.model_rebuild()
StudyRecord.model_rebuild()
ExperimentRecord.model_rebuild()
SignatureRecord.model_rebuild()
TaxonRecord.model_rebuild()
