import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class IdentityEngine:
    def __init__(self):
        # Claimed identity mapping sets
        self.categories = {
            "FAMILY_MEMBER": [
                "i'm your son", "i am your son", "this is your son",
                "i'm your daughter", "i am your daughter", "this is your daughter",
                "i'm your brother", "i am your brother", "this is your brother",
                "i'm your sister", "this is your sister",
                "i'm your dad", "this is dad", "i'm your mom"
            ],
            "BANK": [
                "this is your bank", "i'm from the bank", "from the bank", 
                "bank customer support", "bank representative"
            ],
            "POLICE": [
                "i'm from the police", "i am from the police", "this is the police", "police officer"
            ],
            "GOVERNMENT": [
                "from the government", "tax department", "customs"
            ],
            "EMPLOYER": [
                "i'm your manager", "i am your manager", "this is your boss", "i'm your boss"
            ],
            "CUSTOMER_SUPPORT": [
                "i'm from customer support", "tech support", "from support"
            ]
        }

    def extract_claimed_identity(self, transcript: str) -> Dict[str, Any]:
        transcript_lower = transcript.lower()
        
        for category, phrases in self.categories.items():
            for phrase in phrases:
                if phrase in transcript_lower:
                    logger.info(f"[Identity Engine] Detected claimed identity: {category} (evidence: '{phrase}')")
                    return {
                        "claimed_identity": category,
                        "confidence": 0.91, # MVP deterministic check
                        "evidence": phrase
                    }
                    
        return {
            "claimed_identity": "UNKNOWN",
            "confidence": 0.0,
            "evidence": ""
        }

identity_engine = IdentityEngine()
