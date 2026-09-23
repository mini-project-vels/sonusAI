from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.contact import ContactCreate, ContactResponse
from app.services.contact_service import contact_service

router = APIRouter()

def _to_response(contact) -> ContactResponse:
    return ContactResponse(
        contact_id=contact.contact_id,
        name=contact.name,
        relationship=contact.relationship,
        phone_numbers=contact.phone_numbers,
        trusted=contact.trusted,
        verification_question=contact.verification_question
    )

@router.post("", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    new_contact = contact_service.create_contact(contact)
    return _to_response(new_contact)

@router.get("", response_model=List[ContactResponse])
async def list_contacts():
    contacts = contact_service.list_contacts()
    return [_to_response(c) for c in contacts]

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str):
    contact = contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _to_response(contact)

@router.delete("/{contact_id}")
async def delete_contact(contact_id: str):
    if not contact_service.delete_contact(contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"success": True}

@router.get("/{contact_id}/verification-question")
async def get_verification_question(contact_id: str):
    contact = contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if not contact.verification_question:
        raise HTTPException(status_code=404, detail="No verification configured for this contact")
        
    return {"question": contact.verification_question}
