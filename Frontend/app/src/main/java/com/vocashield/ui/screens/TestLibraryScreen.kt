package com.vocashield.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vocashield.models.CallAnalysis
import com.vocashield.repository.TestAudioRepository
import com.vocashield.repository.TestSample
import com.vocashield.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun TestLibraryScreen(
    onNavigateBack: () -> Unit,
    onNavigateToResult: (CallAnalysis) -> Unit,
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val repo = remember { TestAudioRepository() }
    
    var isLoading by remember { mutableStateOf(true) }
    var runningAnalysisId by remember { mutableStateOf<String?>(null) }
    var samples by remember { mutableStateOf<List<TestSample>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        try {
            val res = repo.getTestSamples()
            samples = res
        } catch (e: Exception) {
            error = e.message
        } finally {
            isLoading = false
        }
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
                Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = TextPrimary)
            }
            Text(
                text = "Test Audio Library",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = PrimaryBlue)
            }
            return
        }
        
        if (error != null) {
            Text("Failed to load test samples: $error", color = HighRiskRed)
            return
        }

        val genuineSamples = samples.filter { it.category == "genuine" }
        val deepfakeSamples = samples.filter { it.category == "deepfake" }

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            if (deepfakeSamples.isNotEmpty()) {
                item {
                    Text("Deepfake Samples", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = HighRiskRed)
                    Spacer(Modifier.height(8.dp))
                }
                items(deepfakeSamples) { sample ->
                    SampleCard(
                        sample = sample,
                        isAnalyzing = runningAnalysisId == sample.id,
                        onAnalyze = {
                            runningAnalysisId = sample.id
                            coroutineScope.launch {
                                val result = repo.analyzeSample(sample.id)
                                runningAnalysisId = null
                                if (result != null) {
                                    onNavigateToResult(result)
                                }
                            }
                        }
                    )
                }
            }
            
            if (genuineSamples.isNotEmpty()) {
                item {
                    Spacer(Modifier.height(8.dp))
                    Text("Genuine Samples", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = LowRiskGreen)
                    Spacer(Modifier.height(8.dp))
                }
                items(genuineSamples) { sample ->
                    SampleCard(
                        sample = sample,
                        isAnalyzing = runningAnalysisId == sample.id,
                        onAnalyze = {
                            runningAnalysisId = sample.id
                            coroutineScope.launch {
                                val result = repo.analyzeSample(sample.id)
                                runningAnalysisId = null
                                if (result != null) {
                                    onNavigateToResult(result)
                                }
                            }
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun SampleCard(
    sample: TestSample,
    isAnalyzing: Boolean,
    onAnalyze: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = SurfaceNavy),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = sample.displayName,
                color = TextPrimary,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.PlayArrow, contentDescription = "Play", tint = PrimaryBlue, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(4.dp))
                LinearProgressIndicator(progress = 0f, modifier = Modifier.weight(1f).height(4.dp), trackColor = BackgroundNavy)
                Spacer(modifier = Modifier.width(8.dp))
                Text("${sample.durationSeconds}s", color = TextSecondary, fontSize = 12.sp)
            }
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = onAnalyze,
                enabled = !isAnalyzing,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
            ) {
                if (isAnalyzing) {
                    CircularProgressIndicator(modifier = Modifier.size(20.dp), color = ColorTextPrimary)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Analyzing audio...")
                } else {
                    Text("Analyze")
                }
            }
        }
    }
}

