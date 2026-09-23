class AttackPatternEngine:
    def classify(self, risk_assessment: dict, scam_signals: dict, context: dict = None) -> list[str]:
        patterns = []
        context = context or {}
        
        voice_fake = risk_assessment.get("voice_risk", 0) >= 60
        
        sig = scam_signals.get("signals", {})
        has_impersonation = sig.get("impersonation", {}).get("detected", False)
        has_financial = sig.get("financial_request", {}).get("detected", False)
        has_credential = sig.get("credential_request", {}).get("detected", False)
        has_urgency = sig.get("urgency", {}).get("detected", False)
        has_payment_redir = sig.get("payment_redirection", {}).get("detected", False)
        has_threat = sig.get("threat_or_pressure", {}).get("detected", False)
        
        claimed = (context.get("claimed_identity") or "UNKNOWN").upper()
        
        # If identity engine flags a claimed identity it effectively counts as impersonation attempt
        if claimed != "UNKNOWN":
            has_impersonation = True

        # Complex Rules
        if voice_fake and has_impersonation:
            patterns.append("AI_VOICE_IMPERSONATION")
            
        if has_financial:
            patterns.append("FINANCIAL_SCAM")
            
        if has_credential:
            patterns.append("OTP_CREDENTIAL_SCAM")
            
        if has_impersonation:
            if claimed in ["BANK", "POLICE", "GOVERNMENT", "EMPLOYER", "CUSTOMER_SUPPORT"] or "bank" in claimed.lower() or "support" in claimed.lower() or "manager" in claimed.lower() or "boss" in claimed.lower():
                patterns.append("AUTHORITY_IMPERSONATION")
            elif claimed in ["FAMILY_MEMBER"] or "son" in claimed.lower() or "daughter" in claimed.lower() or "brother" in claimed.lower():
                patterns.append("FAMILY_IMPERSONATION")
            else:
                # Based on transcript inference if Context claiming is unspecified
                evidence = " ".join(sig.get("impersonation", {}).get("evidence", []))
                if "bank" in evidence or "police" in evidence or "support" in evidence:
                    patterns.append("AUTHORITY_IMPERSONATION")
                if "son" in evidence or "daughter" in evidence or "brother" in evidence:
                    if "AUTHORITY_IMPERSONATION" not in patterns:
                        patterns.append("FAMILY_IMPERSONATION")
                if "AUTHORITY_IMPERSONATION" not in patterns and "FAMILY_IMPERSONATION" not in patterns:
                    patterns.append("AUTHORITY_IMPERSONATION") # generic fallback if bank/police implied
                    
        if has_payment_redir:
            patterns.append("PAYMENT_REDIRECTION")
            
        if has_urgency and (has_financial or has_impersonation or has_threat):
            patterns.append("EMERGENCY_SCAM")
            
        # Specific rule for standard bank impersonation
        if "AUTHORITY_IMPERSONATION" in patterns and has_credential:
            if "BANK_IMPERSONATION" not in patterns:
                patterns.append("BANK_IMPERSONATION")
            
        if not patterns and risk_assessment.get("overall_risk_score", 0) >= 50:
            patterns.append("UNKNOWN_SUSPICIOUS_ACTIVITY")
            
        return list(set(patterns)) # Unique

attack_pattern_engine = AttackPatternEngine()
