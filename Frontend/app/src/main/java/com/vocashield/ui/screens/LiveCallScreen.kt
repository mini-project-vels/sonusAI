package com.vocashield.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CallEnd
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.CallAnalysis
import com.vocashield.ui.components.RiskScore
import com.vocashield.ui.components.SignalCard
import com.vocashield.ui.theme.BackgroundNavy
import com.vocashield.ui.theme.CardSurface
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.MediumRiskOrange
import com.vocashield.ui.theme.PrimaryBlue
import com.vocashield.ui.theme.SurfaceNavy
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

@Composable
fun LiveCallScreen(
    liveCall: CallAnalysis?,
    onNavigateBack: () -> Unit,
    onVerifyCaller: () -> Unit,
    onTriggerRiskAlert: () -> Unit,
    onEndCall: () -> Unit,
    modifier: Modifier = Modifier
) {
    val call = liveCall ?: CallAnalysis(
        callId = "default_live",
        callerName = "Unknown Caller",
        callerNumber = "+91 98765 43210",
        durationSeconds = 24,
        overallRiskScore = 87,
        voiceRiskScore = 82,
        scamRiskScore = 91,
        identityRiskScore = 72,
        claimedIdentity = "Brother"
    )

    // Trigger auto-alert if overall risk score crosses threshold (>= 80)
    LaunchedEffect(call.overallRiskScore) {
        if (call.overallRiskScore >= 80) {
            // onTriggerRiskAlert() // Stay on screen and show recommendations dynamically instead
        }
    }

    val formatDuration = { seconds: Int ->
        val mins = seconds / 60
        val secs = seconds % 60
        String.format("%02d:%02d", mins, secs)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundNavy)
            .padding(16.dp)
    ) {
        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Back",
                    tint = TextPrimary
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Live Call Screening",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.weight(1f))
            Box(
                modifier = Modifier
                    .background(HighRiskRed.copy(alpha = 0.2f), RoundedCornerShape(12.dp))
                    .padding(horizontal = 8.dp, vertical = 4.dp)
            ) {
                Text(
                    text = "● LIVE",
                    color = HighRiskRed,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Caller Info Header
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .background(SurfaceNavy, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = null,
                    tint = TextPrimary,
                    modifier = Modifier.size(36.dp)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = call.callerName,
                color = TextPrimary,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = call.callerNumber,
                color = TextSecondary,
                fontSize = 14.sp
            )
            Text(
                text = formatDuration(call.durationSeconds),
                color = TextSecondary,
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Risk Gauge
        Box(
            modifier = Modifier.fillMaxWidth(),
            contentAlignment = Alignment.Center
        ) {
            RiskScore(score = call.overallRiskScore, size = 170.dp)
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (call.overallRiskScore >= 80) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 20.dp),
                colors = CardDefaults.cardColors(containerColor = com.vocashield.ui.theme.HighRiskRedContainer),
                border = androidx.compose.foundation.BorderStroke(2.dp, HighRiskRed),
                shape = RoundedCornerShape(14.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(text = "🚨", fontSize = 18.sp)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "CRITICAL ACTIONS REQUIRED",
                            color = HighRiskRed,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Black
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // End Call Action
                    Card(
                        colors = CardDefaults.cardColors(containerColor = SurfaceNavy),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth().clickable(onClick = onEndCall)
                    ) {
                        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.CallEnd, contentDescription = null, tint = HighRiskRed)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text("1. End Call Immediately", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                                Text("AASIST Detected High Deepfake Confidence", color = TextSecondary, fontSize = 11.sp)
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Verification Action
                    Card(
                        colors = CardDefaults.cardColors(containerColor = SurfaceNavy),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth().clickable(onClick = onVerifyCaller)
                    ) {
                        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.VerifiedUser, contentDescription = null, tint = PrimaryBlue)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text("2. Ask Secret Question", color = TextPrimary, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                                Text("Challenge caller's claimed identity manually", color = TextSecondary, fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
        }

        // Detailed Breakdown Section
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = SurfaceNavy),
            shape = RoundedCornerShape(14.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Risk Breakdown",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(12.dp))

                RiskMeterRow(label = "Voice Risk (AASIST)", score = call.voiceRiskScore)
                Spacer(modifier = Modifier.height(8.dp))
                RiskMeterRow(label = "Scam Risk (Intent)", score = call.scamRiskScore)
                Spacer(modifier = Modifier.height(8.dp))
                RiskMeterRow(label = "Identity Risk", score = call.identityRiskScore)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Detected Warning Signals Title
        Text(
            text = "Detected Warning Signals",
            color = TextPrimary,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Signals List
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(call.detectedSignals) { signal ->
                SignalCard(signal = signal)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Verification & End Call Actions
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Button(
                onClick = onVerifyCaller,
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
                shape = RoundedCornerShape(10.dp),
                modifier = Modifier.weight(1f)
            ) {
                Icon(imageVector = Icons.Default.VerifiedUser, contentDescription = null)
                Spacer(modifier = Modifier.width(6.dp))
                Text(text = "VERIFY CALLER", fontWeight = FontWeight.Bold)
            }

            OutlinedButton(
                onClick = onEndCall,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = HighRiskRed),
                shape = RoundedCornerShape(10.dp)
            ) {
                Icon(imageVector = Icons.Default.CallEnd, contentDescription = null, tint = HighRiskRed)
                Spacer(modifier = Modifier.width(4.dp))
                Text(text = "END CALL", fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun RiskMeterRow(
    label: String,
    score: Int
) {
    val scoreColor = when {
        score >= 80 -> HighRiskRed
        score >= 35 -> MediumRiskOrange
        else -> LowRiskGreen
    }

    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            color = TextSecondary,
            fontSize = 12.sp,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = "$score%",
            color = scoreColor,
            fontSize = 13.sp,
            fontWeight = FontWeight.Bold
        )
    }
    Spacer(modifier = Modifier.height(4.dp))
    LinearProgressIndicator(
        progress = score / 100f,
        color = scoreColor,
        trackColor = CardSurface,
        modifier = Modifier
            .fillMaxWidth()
            .height(6.dp)
    )
}
