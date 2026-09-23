package com.vocashield.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.ui.theme.CardSurface
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.MediumRiskOrange
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

@Composable
fun RiskTimeline(
    history: List<Int>,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(CardSurface, RoundedCornerShape(12.dp))
            .padding(16.dp)
    ) {
        Text(
            text = "Call Risk Progression",
            color = TextPrimary,
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold
        )
        Text(
            text = "Real-time AI threat score dynamic curve",
            color = TextSecondary,
            fontSize = 11.sp
        )
        Spacer(modifier = Modifier.height(12.dp))

        if (history.isEmpty()) {
            Text(
                text = "No timeline history available",
                color = TextSecondary,
                fontSize = 12.sp
            )
        } else {
            Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(90.dp)
            ) {
                val width = size.width
                val height = size.height
                val stepX = if (history.size > 1) width / (history.size - 1) else width

                // Draw background grid lines (25%, 50%, 75%, 100%)
                listOf(0.25f, 0.5f, 0.75f).forEach { ratio ->
                    drawLine(
                        color = Color(0xFF334155),
                        start = Offset(0f, height * (1 - ratio)),
                        end = Offset(width, height * (1 - ratio)),
                        strokeWidth = 1f
                    )
                }

                // Plot path points
                val path = Path()
                val points = history.mapIndexed { index, score ->
                    val x = index * stepX
                    val y = height - (score / 100f * height)
                    Offset(x, y)
                }

                points.forEachIndexed { i, pt ->
                    if (i == 0) path.moveTo(pt.x, pt.y) else path.lineTo(pt.x, pt.y)
                }

                drawPath(
                    path = path,
                    color = HighRiskRed,
                    style = Stroke(width = 3.dp.toPx())
                )

                // Draw dots
                points.forEachIndexed { idx, pt ->
                    val ptScore = history[idx]
                    val dotColor = when {
                        ptScore >= 80 -> HighRiskRed
                        ptScore >= 35 -> MediumRiskOrange
                        else -> LowRiskGreen
                    }
                    drawCircle(color = dotColor, radius = 5.dp.toPx(), center = pt)
                }
            }
        }
    }
}
