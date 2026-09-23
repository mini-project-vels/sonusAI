class VerificationEngine:
    def generate_recommendations(self, risk_assessment: dict, attack_patterns: list[str], scam_signals: dict) -> list[str]:
        recommendations = []
        
        # Explicit Signal Logic
        sig = scam_signals.get("signals", {})
        has_financial = sig.get("financial_request", {}).get("detected", False)
        has_credential = sig.get("credential_request", {}).get("detected", False)
        has_impersonation = sig.get("impersonation", {}).get("detected", False)
        
        if has_financial:
            recommendations.append("Do not transfer money during the call.")
            
        if has_credential:
            recommendations.append("Never share OTPs, PINs, passwords, or verification codes.")
            
        if has_impersonation:
            recommendations.append("End the call and contact the person using a trusted saved number.")
            
        if risk_assessment.get("voice_risk", 0) >= 60:
            recommendations.append("Voice characteristics indicate possible synthetic or manipulated audio.")
            
        risk_level = risk_assessment.get("risk_level", "LOW")
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendations.append("Do not act on instructions from this caller until their identity is independently verified.")
            
        if not recommendations:
            recommendations.append("No specific defensive action required, but stay cautious.")
            
        return list(dict.fromkeys(recommendations)) # Order preserving unique list

verification_engine = VerificationEngine()
