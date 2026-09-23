import hashlib
from typing import List, Optional
from pydantic import BaseModel

class Contact(BaseModel):
    contact_id: str
    name: str
    relationship: str
    phone_numbers: List[str]
    trusted: bool
    verification_question: Optional[str] = None
    verification_answer_hash: Optional[str] = None

class ContactCreate(BaseModel):
    name: str
    relationship: str
    phone_numbers: List[str]
    trusted: bool = True
    verification_question: Optional[str] = None
    verification_answer: Optional[str] = None  # Plaintext, will be hashed

class ContactResponse(BaseModel):
    contact_id: str
    name: str
    relationship: str
    phone_numbers: List[str]
    trusted: bool
    verification_question: Optional[str] = None

def hash_answer(answer: str) -> str:
    # MVP naive hashing. For prod, use passlib/bcrypt
    if not answer:
        return ""
    normalized = answer.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
