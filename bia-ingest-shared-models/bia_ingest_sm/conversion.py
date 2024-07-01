from typing import List, Any, Dict, Optional
from .biostudies import Submission, attributes_to_dict, Section, Attribute
from .shared_models import Study, Organisation, Agent 
from src.bia_models import bia_data_model, semantic_models

def get_study_from_submission(submission: Submission) -> Study:
    """Return an API study model populated from the submission

    """
    
    submission_attributes = attributes_to_dict(submission.attributes)
    authors = find_and_convert_authors(submission)
    study_dict = {
        "accession_id": submission.accno,
        "release_date": submission_attributes["ReleaseDate"],
        "title": submission_attributes.get("Title", ""),
        "author": authors,
        "file_reference_count": 0,
        "image_count": 0,
    }
    study = Study.model_validate(study_dict)

    return study

def get_affiliation(submission: Submission) -> Dict[str, semantic_models.Affiliation]:
    """Maps biostudies.Organisation sections to semantic_models.Affiliations

    """

    organisation_sections = find_sections_recursive(
        submission.section, ["organisation", "organization"], []
    )

    key_mapping = [
        ("display_name", "Name", None),
        ("rorid", "RORID", None),
        # TODO: Address does not exist in current biostudies.Organisation
        ("address", "Address", None),
        # TODO:  does not exist in current biostudies.Organisation
        ("website", "Website", None),
    ]

    affiliation_dict = {}
    for section in organisation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        affiliation_dict[section.accno] = semantic_models.Affiliation.model_validate(model_dict)

    return affiliation_dict


def get_contributor(submission: Submission) -> List[semantic_models.Contributor]:
    """ Map authors in submission to semantic_model.Contributors

    """
    affiliation_dict = get_affiliation(submission) 
    key_mapping = [
        ("display_name", "Name", None),
        ("contact_email", "E-mail", "not@supplied.com"),
        ("role", "Role", None),
        ("orcid", "ORCID", None),
        ("affiliation", "affiliation", []),
    ]
    author_sections = find_sections_recursive(submission.section, ["author",], [])
    contributors = []
    for section in author_sections:
        attr_dict = mattributes_to_dict(section.attributes, affiliation_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        # TODO: Find out if authors can have more than one organisation ->
        #       what are the implications for mattributes_to_dict?
        if model_dict["affiliation"] is None:
            model_dict["affiliation"] = []
        elif type(model_dict["affiliation"]) is not list:
            model_dict["affiliation"] = [model_dict["affiliation"],]
        contributors.append(semantic_models.Contributor.model_validate(model_dict))

    return contributors
    

def find_sections_recursive(
    section: Section, search_types: List[str], results: Optional[List[Section]] = []
) -> List[Section]:
    """Find all sections of search_types within tree, starting at given section

    """

    search_types_lower = [ s.lower() for s in search_types ]
    if section.type.lower() in search_types_lower:
        results.append(section)

    # Each thing in section.subsections is either Section or List[Section]
    # First, let's make sure we ensure they're all lists:
    nested = [
        [item] if not isinstance(item, list) else item for item in section.subsections
    ]
    # Then we can flatten this list of lists:
    flattened = sum(nested, [])

    for section in flattened:
        find_sections_recursive(section, search_types, results)

    return results

def find_and_convert_authors(submission: Submission) -> List[Agent]:
    """Return API models of authors in submission

    """
    organisation_sections = find_sections_recursive(
        submission.section, ["organisation", "organization"], []
    )

    key_mapping = [
        ("display_name", "Name", None),
        ("rorid", "RORID", None),
        # TODO: Agent in shared models needs emailStr to be optional
        ("contact_email", "E-mail", "not@supplied.com"),
    ]

    organisation_dict = {}
    for section in organisation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        organisation_dict[section.accno] = Organisation.model_validate(model_dict)

    key_mapping = [
        ("display_name", "Name", "Not supplied"),
        ("contact_email", "E-mail", "not@supplied.com"),
        # TODO: Agent/Person or maybe create a new Author class for this
        # in shared models?
        #("role", "Role", None),
        ("memberOf", "affiliation", []),
        # TODO: Nowhere to store orcid in Agent. Need Person?
        #("orcid", "ORCID", None),
    ]
    author_sections = find_sections_recursive(submission.section, ["author",], [])
    authors = []
    for section in author_sections:
        attr_dict = mattributes_to_dict(section.attributes, organisation_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        # TODO: Find out if authors can have more than one
        # organisation ->what are the implications for mattributes_to_dict?
        if model_dict["memberOf"] is None:
            model_dict["memberOf"] = []
        elif type(model_dict["memberOf"]) is not list:
            model_dict["memberOf"] = [model_dict["memberOf"],]
        authors.append(Agent.model_validate(model_dict))

    return authors

# TODO check type of reference_dict. Possibly Dict[str, str], but need to
# verify. This also determines type returned by function
def mattributes_to_dict(attributes: List[Attribute], reference_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return attributes as dictionary dereferencing attribute references

    Return the list of attributes supplied as a dictionary. Any attributes
    whose values are references are 'dereferenced' using the reference_dict
    """
    def value_or_dereference(attr):
        if attr.reference:
            return reference_dict[attr.value]
        else:
            return attr.value

    return {attr.name: value_or_dereference(attr) for attr in attributes}
