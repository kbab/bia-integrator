from bia_ingest_sm.shared_models import Organisation

def test_organisation():
    organisation = Organisation(
        **{ 
            "display_name": "Test",
            "contact_email": "test@test.com",
            "rorid": "Test org",
            "address": "Test address",
        }
    )

    assert type(organisation) == Organisation
