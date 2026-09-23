package com.vocashield.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.CallEnd
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Help
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.TrustedContact
import com.vocashield.ui.components.VerificationCard
import com.vocashield.ui.theme.BackgroundNavy
import com.vocashield.ui.theme.CardSurface
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.PrimaryBlue
import com.vocashield.ui.theme.SurfaceNavy
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

@Composable
fun VerificationScreen(
    claimedIdentity: String = "Brother",
    trustedContact: TrustedContact? = null,
    onNavigateBack: () -> Unit,
    onEndCall: () -> Unit,
    onManualCall: (String) -> Unit,
    onMarkVerified: () -> Unit,
    modifier: Modifier = Modifier
) {
    val question = trustedContact?.verificationQuestion ?: "What was the name of our childhood pet?"

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
                text = "Identity Verification",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Claimed Identity Card
        VerificationCard(
            claimedIdentity = claimedIdentity,
            question = question
        )

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "Recommended Safety Protocol",
            color = TextPrimary,
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(12.dp))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            item {
                ActionStepCard(
                    stepNumber = "1",
                    title = "End the call immediately",
                    description = "Do not transfer money or share passwords over suspicious calls.",
                    icon = Icons.Default.CallEnd,
                    tint = HighRiskRed,
                    onClick = onEndCall
                )
            }
            item {
                ActionStepCard(
                    stepNumber = "2",
                    title = "Call the trusted number manually",
                    description = "Use a saved contact line (${trustedContact?.phoneNumber ?: "+91 98765 33333"}) to verify directly.",
                    icon = Icons.Default.Call,
                    tint = PrimaryBlue,
                    onClick = { onManualCall(trustedContact?.phoneNumber ?: "+91 98765 33333") }
                )
            }
            item {
                ActionStepCard(
                    stepNumber = "3",
                    title = "Ask your private verification question",
                    description = "Ask: \"$question\"",
                    icon = Icons.Default.Help,
                    tint = LowRiskGreen,
                    onClick = {}
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        Button(
            onClick = onMarkVerified,
            colors = ButtonDefaults.buttonColors(containerColor = LowRiskGreen),
            shape = RoundedCornerShape(10.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
        ) {
            Icon(imageVector = Icons.Default.CheckCircle, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text(text = "MARK CALL AS VERIFIED SAFE", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun ActionStepCard(
    stepNumber: String,
    title: String,
    description: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    tint: androidx.compose.ui.graphics.Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = CardSurface),
        shape = RoundedCornerShape(12.dp),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .background(SurfaceNavy, RoundedCornerShape(8.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = tint,
                    modifier = Modifier.size(20.dp)
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "$stepNumber. $title",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = description,
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
        }
    }
}
