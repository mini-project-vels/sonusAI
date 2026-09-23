import pytest
from app.services.contact_service import contact_service
from app.models.contact import ContactCreate

def test_contact_crud():
    c = ContactCreate(name="Arun", relationship="brother", phone_numbers=["+919876543210"], trusted=True, verification_question="Pet?")
    contact = contact_service.create_contact(c)
    assert contact.contact_id.startswith("CONTACT_")
    
    fetched = contact_service.get_contact(contact.contact_id)
    assert fetched.name == "Arun"
    
    found = contact_service.find_by_phone_number("+919876543210")
    assert found is not None
    assert found.contact_id == contact.contact_id
    
    deleted = contact_service.delete_contact(contact.contact_id)
    assert deleted is True
    assert contact_service.get_contact(contact.contact_id) is None
