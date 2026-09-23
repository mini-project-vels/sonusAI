package com.vocashield.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.RiskLevel
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.HighRiskRedContainer
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.LowRiskGreenContainer
import com.vocashield.ui.theme.MediumRiskOrange
import com.vocashield.ui.theme.MediumRiskOrangeContainer

@Composable
fun RiskBadge(
    riskLevel: RiskLevel,
    score: Int? = null,
    modifier: Modifier = Modifier
) {
    val (bgColor, textColor, label) = when (riskLevel) {
        RiskLevel.LOW -> Triple(LowRiskGreenContainer, LowRiskGreen, "LOW")
        RiskLevel.MEDIUM -> Triple(MediumRiskOrangeContainer, MediumRiskOrange, "MEDIUM")
        RiskLevel.HIGH -> Triple(HighRiskRedContainer, HighRiskRed, "HIGH")
        RiskLevel.CRITICAL -> Triple(HighRiskRedContainer, HighRiskRed, "CRITICAL")
    }

    Box(
        modifier = modifier
            .background(bgColor, RoundedCornerShape(12.dp))
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(
            text = if (score != null) "$label $score/100" else label,
            color = textColor,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.5.sp
        )
    }
}
