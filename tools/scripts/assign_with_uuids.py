import uuid
import logging
import hashlib
from typing import List 

import click
from bia_integrator_core.models import BIAStudy, FileReference, Author
from bia_integrator_core.interface import persist_study

from bia_integrator_tools.biostudies import (
    File,
    Submission,
    Section,
    attributes_to_dict,
    load_submission,
    find_files_in_submission
)


logger = logging.getLogger(__file__)


def bst_file_to_id(accession_id: str, bst_file: File):

    hash_input = accession_id
    hash_input += str(bst_file.path)
    hash_input += str(bst_file.size)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    id_as_uuid = uuid.UUID(version=4, hex=hexdigest)

    return str(id_as_uuid)


def test_bst_file_to_uuid():

    first_bst_file = File(path="file1.tif", size=123)
    second_bst_file = File(path="file2.tif", size=456)
    third_bst_file = File(path="file2.tif", size=789)

    # id is a string
    id = bst_file_to_id(accession_id="foo1", bst_file=first_bst_file)
    assert isinstance(id, str)

    # Same accession, same file, same size should produce same id
    first_id = bst_file_to_id(accession_id="foo1", bst_file=first_bst_file)
    second_id = bst_file_to_id(accession_id="foo1", bst_file=first_bst_file)
    assert first_id == second_id

    # Same accession, different filename should produce different ids
    first_id = bst_file_to_id(accession_id="foo1", bst_file=first_bst_file)
    second_id = bst_file_to_id(accession_id="foo1", bst_file=second_bst_file)
    assert first_id != second_id

    # Different accession, same filename should produce different ids
    first_id = bst_file_to_id(accession_id="foo1", bst_file=first_bst_file)
    second_id = bst_file_to_id(accession_id="foo2", bst_file=first_bst_file)
    assert first_id != second_id

    # Same accession, same filename, different size should produce different ids
    first_id = bst_file_to_id(accession_id="foo1", bst_file=second_bst_file)
    second_id = bst_file_to_id(accession_id="foo1", bst_file=third_bst_file)
    assert first_id != second_id


def bst_file_to_file_reference(accession_id: str, bst_file: File) -> FileReference:

    fileref_id = bst_file_to_id(accession_id, bst_file)
    fileref_name = str(bst_file.path)
    fileref_attributes = attributes_to_dict(bst_file.attributes)

    fileref = FileReference(
        id=fileref_id,
        name=fileref_name,
        size_in_bytes=bst_file.size,
        attributes=fileref_attributes
    )

    return fileref


def filerefs_from_bst_submission(submission: Submission) -> List[FileReference]:

    all_files = find_files_in_submission(submission)

    logger.info(f"Creating references for {len(all_files)} files")
    accession_id = submission.accno
    filerefs = [bst_file_to_file_reference(accession_id, bst_file) for bst_file in all_files]

    return filerefs


def author_section_to_author(author_section: Section) -> Author:

    attributes_dict = attributes_to_dict(author_section.attributes)
    
    return Author(name=attributes_dict['Name'])


def find_authors_in_submission(submission: Submission):
    
    authors = []
    for section in submission.section.subsections:
        if section.type == 'Author' or section.type == 'author':
            authors.append(author_section_to_author(section))
            
    return authors    


def study_title_from_submission(submission: Submission) -> str:

    submission_attr_dict = attributes_to_dict(submission.attributes)

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    return study_title


def imaging_method_from_submission(submission: Submission) -> str:

    study_components = [
        section
        for section in submission.section.subsections
        if section.type == 'Study Component'
    ]

    if len(study_components):
        study_component_attr_dict = attributes_to_dict(study_components[0].attributes)
        imaging_method = study_component_attr_dict.get('Imaging Method', "Unknown")
    else:
        imaging_method = "Unknown"

    return imaging_method


def bst_submission_to_bia_study(submission: Submission) -> BIAStudy:

    accession_id = submission.accno
    filerefs = filerefs_from_bst_submission(submission)
    study_title = study_title_from_submission(submission)
    imaging_method = imaging_method_from_submission(submission)

    study_section_attr_dict = attributes_to_dict(submission.section.attributes)
    submission_attr_dict = attributes_to_dict(submission.attributes)
    bia_study = BIAStudy(
        accession_id=accession_id,
        title=study_title,
        authors=find_authors_in_submission(submission),
        release_date=submission_attr_dict['ReleaseDate'],
        description=study_section_attr_dict['Description'],
        organism=study_section_attr_dict.get('Organism', "Unknown"),
        imaging_type=imaging_method,
        file_references=filerefs
    )

    return bia_study


@click.command()
@click.argument("accession_id")
def main(accession_id):
    
    logging.basicConfig(level=logging.INFO)

    bst_submission = load_submission(accession_id)
    bia_study = bst_submission_to_bia_study(bst_submission)

    persist_study(bia_study)


if __name__ == "__main__":
    main()