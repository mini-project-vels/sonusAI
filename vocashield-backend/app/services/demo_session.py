# app/services/demo_session.py
import json
import logging
from app.engines.risk_engine import risk_engine
from app.engines.identity_engine import identity_engine
from app.engines.attack_pattern_engine import attack_pattern_engine
from app.engines.verification_engine import verification_engine
from app.engines.scam_signal_engine import signal_engine

logger = logging.getLogger(__name__)

class DemoSession:
    """Controlled backend behavior validator testing Scenarios A, B, and C strictly matching Android demands."""
    
    @staticmethod
    def run_scenario(name: str, fake_prob: float, transcript: str, number_known: bool, trusted: bool, claimed_category: str = "UNKNOWN"):
        
        deepfake_result = {
            "fake_probability": fake_prob,
            "real_probability": 1.0 - fake_prob,
            "prediction": "FAKE" if fake_prob > 0.5 else "REAL"
        }
        
        scam_result = signal_engine.analyze(transcript)
        identity_result = identity_engine.extract_claimed_identity(transcript)
        
        # Merge claiming
        claimed = identity_result["claimed_identity"] if identity_result["claimed_identity"] != "UNKNOWN" else claimed_category
        
        context = {
            "number_known": number_known,
            "trusted_contact": trusted,
            "claimed_identity": claimed,
            "verification_status": "NOT_AVAILABLE"
        }
        
        risk_metrics = risk_engine.calculate_risk(deepfake_result, scam_result, context)
        patterns = attack_pattern_engine.classify(risk_metrics, scam_result, context)
        
        print(f"\n{'='*50}\nSCENARIO: {name}\n{'-'*50}")
        print(f"Auth Risk: {'HIGH' if deepfake_result['prediction'] == 'FAKE' else 'LOW'} (Prob: {fake_prob})")
        print(f"Scam Risk: {'HIGH' if scam_result['scam_behavior_score'] >= 50 else 'LOW'} (Score: {scam_result['scam_behavior_score']})")
        print(f"Identity : {'HIGH' if risk_metrics['identity']['identity_risk'] >= 50 else 'LOW'} (Score: {risk_metrics['identity']['identity_risk']})")
        print(f"Overall  : {risk_metrics['risk_level']} (Score: {risk_metrics['overall_risk_score']})")
        print(f"Patterns : {patterns}")

    @classmethod
    def test_all(cls):
        # Scenario A — AI Family Scam
        # AI voice, claims brother, emergency, transfer money
        cls.run_scenario(
            "A - AI Family Scam",
            fake_prob=0.99,
            transcript="I'm your brother. I'm in an emergency. Send me the money immediately.",
            number_known=False,
            trusted=False
        )
        
        # Scenario B — Human Scam
        # Human voice, bank impersonation, urgency, OTP request
        cls.run_scenario(
            "B - Human Scam",
            fake_prob=0.01,
            transcript="This is your bank. Your account has an emergency. Read me the OTP.",
            number_known=False,
            trusted=False
        )
        
        # Scenario C — AI Voice but Harmless
        # AI voice, harmless conversation
        cls.run_scenario(
            "C - AI Voice Harmless",
            fake_prob=0.96,
            transcript="Hey, just planning out the schedule for tomorrow. See you then.",
            number_known=True,
            trusted=True
        )

if __name__ == "__main__":
    DemoSession.test_all()
