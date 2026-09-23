package com.vocashield.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.CallAnalysis
import com.vocashield.models.RiskLevel
import com.vocashield.ui.components.CallCard
import com.vocashield.ui.theme.BackgroundNavy
import com.vocashield.ui.theme.CardSurface
import com.vocashield.ui.theme.HighRiskRed
import com.vocashield.ui.theme.LowRiskGreen
import com.vocashield.ui.theme.PrimaryBlue
import com.vocashield.ui.theme.TextPrimary

@Composable
fun CallHistoryScreen(
    calls: List<CallAnalysis>,
    onSelectCall: (CallAnalysis) -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedFilter by remember { mutableStateOf("ALL") }

    val filteredCalls = remember(calls, selectedFilter) {
        when (selectedFilter) {
            "HIGH" -> calls.filter { it.riskLevel == RiskLevel.HIGH || it.riskLevel == RiskLevel.CRITICAL }
            "LOW" -> calls.filter { it.riskLevel == RiskLevel.LOW }
            else -> calls
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundNavy)
            .padding(16.dp)
    ) {
        Text(
            text = "Call History Logs",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Full logs of AI-screened call activity",
            color = com.vocashield.ui.theme.TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Filter chips
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilterChip(
                selected = selectedFilter == "ALL",
                onClick = { selectedFilter = "ALL" },
                label = { Text("All (${calls.size})") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = PrimaryBlue,
                    selectedLabelColor = TextPrimary,
                    containerColor = CardSurface
                )
            )
            FilterChip(
                selected = selectedFilter == "HIGH",
                onClick = { selectedFilter = "HIGH" },
                label = { Text("High Risk") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = HighRiskRed,
                    selectedLabelColor = TextPrimary,
                    containerColor = CardSurface
                )
            )
            FilterChip(
                selected = selectedFilter == "LOW",
                onClick = { selectedFilter = "LOW" },
                label = { Text("Safe / Low") },
                colors = FilterChipDefaults.filterChipColors(
                    selectedContainerColor = LowRiskGreen,
                    selectedLabelColor = TextPrimary,
                    containerColor = CardSurface
                )
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.weight(1f)
        ) {
            items(filteredCalls) { call ->
                CallCard(
                    call = call,
                    onClick = { onSelectCall(call) }
                )
            }
        }
    }
}
