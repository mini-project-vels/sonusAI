class RiskEngine:
    def __init__(self):
        self.weights = {
            "voice_risk": 0.35,
            "scam_behavior_risk": 0.40,
            "identity_risk": 0.15,
            "context_risk": 0.10
        }

    def _determine_contribution(self, score: int) -> str:
        if score >= 75: return "HIGH"
        if score >= 50: return "MEDIUM"
        return "LOW"

    def calculate_risk(self, deepfake_result: dict, scam_analysis: dict, context: dict = None) -> dict:
        context = context or {}
        
        # Voice Risk
        fake_prob = deepfake_result.get("fake_probability", 0.0)
        voice_risk = int(fake_prob * 100)
        
        # Scam Behavior Risk
        scam_behavior_risk = scam_analysis.get("scam_behavior_score", 0)
        
        # Context extraction
        number_known = context.get("number_known", False)
        trusted_contact = context.get("trusted_contact", False)
        claimed_identity = context.get("claimed_identity", "UNKNOWN")
        verification_status = context.get("verification_status", "NOT_AVAILABLE")
        
        # Identity match logic
        # It's a match if they are a trusted contact calling from a known trusted number
        # AND they claimed a role that matches (or we assume match for MVP).
        # We define a "mismatch" if the number is NOT known, but they claim to be family.
        identity_match = True
        
        # Identity Risk
        if number_known and trusted_contact:
            identity_risk = 10
        elif not number_known and trusted_contact:
            identity_risk = 70
        elif not number_known and not trusted_contact:
            identity_risk = 40
        else:
            identity_risk = 20
            
        if claimed_identity != "UNKNOWN" and not number_known:
            identity_risk = min(identity_risk + 50, 100)
            identity_match = False
            
        if verification_status == "FAILED":
            identity_risk = 100
            identity_match = False
        elif verification_status == "PASSED":
            identity_risk = max(0, identity_risk - 50)
            identity_match = True
            
        # Context Risk
        context_risk = 0
        if not number_known:
            context_risk += 30
        else:
            context_risk += 5
            
        if trusted_contact:
            context_risk = max(context_risk - 20, 0)
            
        if claimed_identity != "UNKNOWN" and not number_known:
            context_risk = min(context_risk + 40, 100)
            
        # Ensure clamped
        identity_risk = max(0, min(100, identity_risk))
        context_risk = max(0, min(100, context_risk))
        
        # Calculate Overall Score (clamped)
        overall = (
            self.weights["voice_risk"] * voice_risk +
            self.weights["scam_behavior_risk"] * scam_behavior_risk +
            self.weights["identity_risk"] * identity_risk +
            self.weights["context_risk"] * context_risk
        )
        overall_risk_score = max(0, min(100, int(round(overall))))
        
        # Calculate Level
        if overall_risk_score < 25:
            risk_level = "LOW"
        elif overall_risk_score < 50:
            risk_level = "MEDIUM"
        elif overall_risk_score < 75:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
            
        # Explainability List generating mapping
        risk_factors = []
        if voice_risk >= 50:
            risk_factors.append({
                "factor": "Synthetic voice characteristics",
                "score": voice_risk,
                "contribution": self._determine_contribution(voice_risk)
            })
            
        # Correlate specific scam signals
        signals = scam_analysis.get("signals", {})
        for name, data in signals.items():
            if data["detected"]:
                score_mapping = int(data["confidence"] * 100)
                if score_mapping > 0:
                    text_label = name.replace("_", " ").capitalize()
                    risk_factors.append({
                        "factor": text_label,
                        "score": score_mapping,
                        "contribution": self._determine_contribution(score_mapping)
                    })
                    
        # Context factors
        if not number_known:
            risk_factors.append({
                "factor": "Unknown phone number",
                "score": 40,
                "contribution": "MEDIUM" if identity_risk < 75 else "HIGH"
            })
            
        if claimed_identity != "UNKNOWN" and not number_known:
            risk_factors.append({
                "factor": "Caller claims to be a trusted contact from an unknown number",
                "score": identity_risk,
                "contribution": "HIGH"
            })
            
        if verification_status == "FAILED":
             risk_factors.append({
                 "factor": "Verification challenge failed",
                 "score": 100,
                 "contribution": "HIGH"
             })
        elif verification_status == "NOT_AVAILABLE" and identity_risk >= 50:
             risk_factors.append({
                 "factor": "Private verification not completed",
                 "score": identity_risk,
                 "contribution": "MEDIUM"
             })
             
        return {
            "voice_risk": voice_risk,
            "scam_behavior_risk": scam_behavior_risk,
            "context_risk": context_risk,
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "identity": {
                "known_number": number_known,
                "trusted_contact": trusted_contact,
                "claimed_identity": claimed_identity,
                "identity_match": identity_match,
                "identity_risk": identity_risk,
                "verification_status": verification_status
            }
        }

risk_engine = RiskEngine()
