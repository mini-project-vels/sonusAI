package com.vocashield.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.MediumRiskOrange
import com.vocashield.ui.theme.SurfaceNavy
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

@Composable
fun RiskScore(
    score: Int,
    modifier: Modifier = Modifier,
    size: Dp = 180.dp,
    strokeWidth: Dp = 14.dp
) {
    val scoreColor by animateColorAsState(
        targetValue = when {
            score >= 80 -> HighRiskRed
            score >= 60 -> HighRiskRed
            score >= 35 -> MediumRiskOrange
            else -> LowRiskGreen
        },
        animationSpec = tween(durationMillis = 600),
        label = "scoreColor"
    )

    val animatedSweepAngle by animateFloatAsState(
        targetValue = (score / 100f) * 280f,
        animationSpec = tween(durationMillis = 800),
        label = "sweepAngle"
    )

    Box(
        modifier = modifier
            .size(size)
            .shadow(16.dp, CircleShape, spotColor = scoreColor),
        contentAlignment = Alignment.Center
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val startAngle = 130f
            val sweepAngle = 280f

            // Background Arc Track
            drawArc(
                color = Color(0xFF1E293B),
                startAngle = startAngle,
                sweepAngle = sweepAngle,
                useCenter = false,
                style = Stroke(width = strokeWidth.toPx(), cap = StrokeCap.Round)
            )

            // Animated Active Score Arc
            drawArc(
                brush = Brush.sweepGradient(
                    listOf(scoreColor.copy(alpha = 0.6f), scoreColor)
                ),
                startAngle = startAngle,
                sweepAngle = animatedSweepAngle,
                useCenter = false,
                style = Stroke(width = strokeWidth.toPx(), cap = StrokeCap.Round)
            )
        }

        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "$score",
                fontSize = (size.value * 0.28).sp,
                fontWeight = FontWeight.ExtraBold,
                color = scoreColor
            )
            Text(
                text = "/100",
                fontSize = 12.sp,
                color = TextSecondary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = when {
                    score >= 80 -> "CRITICAL RISK"
                    score >= 60 -> "HIGH RISK"
                    score >= 35 -> "MEDIUM RISK"
                    else -> "LOW RISK"
                },
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = scoreColor,
                letterSpacing = 1.sp
            )
        }
    }
}
