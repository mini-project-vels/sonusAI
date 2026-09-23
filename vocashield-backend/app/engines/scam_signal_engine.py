import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ScamSignalEngine:
    def __init__(self):
        # Weights normalized to sum slightly over 100 or exactly 100.
        # It's out of 100.
        self.weights = {
            "financial_request": 25,
            "credential_request": 25,
            "urgency": 15,
            "secrecy": 10,
            "impersonation": 10,
            "threat_or_pressure": 10,
            "payment_redirection": 5
        }
        
        # Transparent, deterministic keyword maps. We normalize text to lowercase for checks.
        self.signatures = {
            "financial_request": [
                "transfer money", "send money", "bank transfer", "upi", 
                "payment", "account", "investment", "loan", "gift card", "cryptocurrency", "rupees"
            ],
            "credential_request": [
                "otp", "verification code", "pin", "password", "cvv", 
                "card number", "login", "security code"
            ],
            "urgency": [
                "immediately", "right now", "urgent", "emergency", 
                "quickly", "don't delay", "act now"
            ],
            "secrecy": [
                "don't tell anyone", "keep this secret", "don't tell your parents", 
                "don't tell your boss", "don't tell the bank"
            ],
            "impersonation": [
                "hi son", "i'm your son", "i am your son", "i'm your daughter", "i'm your brother",
                "i am your brother", "i am your daughter", "i'm your manager", 
                "i'm your boss", "i'm from the bank", "this is your bank", 
                "i'm from the police", "i'm from customer support", "bank customer support"
            ],
            "threat_or_pressure": [
                "account will be blocked", "police will come", "legal action", 
                "arrest", "fine", "penalty", "account suspension"
            ],
            "payment_redirection": [
                "send it to this number", "use this upi id", "transfer to another account", 
                "scan this qr", "click this payment link", "send the payment to this upi"
            ]
        }

    def analyze(self, transcript: str) -> Dict[str, Any]:
        transcript_lower = transcript.lower()
        signals = {}
        total_score = 0
        
        for category, keywords in self.signatures.items():
            evidence = []
            for kw in keywords:
                if kw in transcript_lower:
                    evidence.append(kw)
                    
            detected = len(evidence) > 0
            
            # Simple static confidence mapped to weight existence
            # In MVP, confidence is high if evidence exists.
            confidence = 0.0
            if detected:
                confidence = round(min(0.5 + (len(evidence) * 0.2), 0.99), 2)
                total_score += self.weights[category]
                
            signals[category] = {
                "detected": detected,
                "confidence": confidence,
                "evidence": evidence
            }
            
        final_score = min(total_score, 100)
        
        # Development Diagnostics
        logger.info("[Scam Analysis]")
        logger.info(f"Financial request: {signals['financial_request']['detected']}")
        logger.info(f"Credential request: {signals['credential_request']['detected']}")
        logger.info(f"Urgency: {signals['urgency']['detected']}")
        logger.info(f"Secrecy: {signals['secrecy']['detected']}")
        logger.info(f"Impersonation: {signals['impersonation']['detected']}")
        logger.info(f"Threat: {signals['threat_or_pressure']['detected']}")
        logger.info(f"Payment redirection: {signals['payment_redirection']['detected']}")
        logger.info(f"Scam behavior score: {final_score}")
            
        return {
            "scam_behavior_score": final_score,
            "signals": signals
        }

signal_engine = ScamSignalEngine()
