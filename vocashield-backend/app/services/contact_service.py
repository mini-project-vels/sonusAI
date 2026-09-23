import uuid
from typing import List, Optional
from app.models.contact import Contact, ContactCreate, hash_answer

class ContactService:
    def __init__(self):
        self._contacts = {}
        
    def _normalize_phone(self, phone: str) -> str:
        # Strip spaces and formatting for simple matching
        return "".join(c for c in phone if c.isdigit() or c == "+")

    def create_contact(self, contact_data: ContactCreate) -> Contact:
        contact_id = f"CONTACT_{uuid.uuid4().hex[:8].upper()}"
        
        answer_hash = None
        if contact_data.verification_answer:
            answer_hash = hash_answer(contact_data.verification_answer)
            
        normalized_phones = [self._normalize_phone(p) for p in contact_data.phone_numbers]
            
        contact = Contact(
            contact_id=contact_id,
            name=contact_data.name,
            relationship=contact_data.relationship,
            phone_numbers=normalized_phones,
            trusted=contact_data.trusted,
            verification_question=contact_data.verification_question,
            verification_answer_hash=answer_hash
        )
        
        self._contacts[contact_id] = contact
        return contact

    def get_contact(self, contact_id: str) -> Optional[Contact]:
        return self._contacts.get(contact_id)

    def list_contacts(self) -> List[Contact]:
        return list(self._contacts.values())
        
    def find_by_phone_number(self, phone_number: str) -> Optional[Contact]:
        if not phone_number:
            return None
        normalized_query = self._normalize_phone(phone_number)
        for contact in self._contacts.values():
            if normalized_query in contact.phone_numbers:
                return contact
        return None

    def delete_contact(self, contact_id: str) -> bool:
        if contact_id in self._contacts:
            del self._contacts[contact_id]
            return True
        return False
        
contact_service = ContactService()
