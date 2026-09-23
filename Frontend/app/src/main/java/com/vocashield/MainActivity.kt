package com.vocashield

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.vocashield.navigation.AppNavigation
import com.vocashield.repository.MockCallRepository
import com.vocashield.ui.theme.VocaShieldTheme

class MainActivity : ComponentActivity() {

    // Use 10.0.2.2 for emulator (maps to laptop localhost)
    // Change to your laptop's local IP if using a physical device
    // e.g. "192.168.1.X:8000"
    private val backendUrl = "127.0.0.1:8000"

    private val callRepository by lazy { MockCallRepository(applicationContext, backendUrl) }

    private val requestMicPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        // Permission result handled — WebSocketManager checks at runtime
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Request mic permission upfront
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            requestMicPermission.launch(Manifest.permission.RECORD_AUDIO)
        }

        setContent {
            VocaShieldTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppNavigation(repository = callRepository)
                }
            }
        }
    }
}
