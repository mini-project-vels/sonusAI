package com.vocashield.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.RiskLevel
import com.vocashield.models.RiskSignal
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.MediumRiskOrange
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

@Composable
fun SignalCard(
    signal: RiskSignal,
    modifier: Modifier = Modifier
) {
    val accentColor = when (signal.severity) {
        RiskLevel.CRITICAL, RiskLevel.HIGH -> HighRiskRed
        RiskLevel.MEDIUM -> MediumRiskOrange
        else -> MediumRiskOrange
    }

    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(Color(0xFF161F32), RoundedCornerShape(10.dp))
            .border(1.dp, accentColor.copy(alpha = 0.4f), RoundedCornerShape(10.dp))
            .padding(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Default.Warning,
            contentDescription = null,
            tint = accentColor,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(12.dp))
        Column {
            Text(
                text = signal.title,
                color = TextPrimary,
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold
            )
            if (signal.description.isNotEmpty()) {
                Text(
                    text = signal.description,
                    color = TextSecondary,
                    fontSize = 11.sp
                )
            }
        }
    }
}
