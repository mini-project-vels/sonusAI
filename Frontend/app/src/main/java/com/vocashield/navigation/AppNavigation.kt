package com.vocashield.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.vocashield.models.CallAnalysis
import com.vocashield.repository.CallRepository
import com.vocashield.ui.screens.AddTrustedContactScreen
import com.vocashield.ui.screens.CallHistoryScreen
import com.vocashield.ui.screens.CallResultScreen
import com.vocashield.ui.screens.HomeScreen
import com.vocashield.ui.screens.LandingScreen
import com.vocashield.ui.screens.LiveCallScreen
import com.vocashield.ui.screens.RiskAlertScreen
import com.vocashield.ui.screens.SettingsScreen
import com.vocashield.ui.screens.TrustedContactsScreen
import com.vocashield.ui.screens.VerificationScreen
import com.vocashield.ui.theme.BackgroundNavy
import com.vocashield.ui.theme.BorderNavy
import com.vocashield.ui.theme.CardSurface
import com.vocashield.ui.theme.PrimaryBlue
import com.vocashield.ui.theme.SurfaceNavy
import com.vocashield.ui.theme.TextPrimary
import com.vocashield.ui.theme.TextSecondary

sealed class NavRoute(val route: String, val title: String? = null, val icon: ImageVector? = null) {
    object Landing : NavRoute("landing")
    object Home : NavRoute("home", "Home", Icons.Default.Home)
    object Calls : NavRoute("calls", "Calls", Icons.Default.Phone)
    object Trusted : NavRoute("trusted", "Trust", Icons.Default.Shield)

    object LiveCall : NavRoute("live_call")
    object RiskAlert : NavRoute("risk_alert")
    object Verification : NavRoute("verification")
    object CallResult : NavRoute("call_result")
    object AddTrustedContact : NavRoute("add_trusted")
    object Settings : NavRoute("settings")
}

@Composable
fun AppNavigation(repository: CallRepository) {
    val navController = rememberNavController()

    val liveCallState by repository.liveCallState.collectAsState()
    val recentCalls by repository.recentCallsState.collectAsState()
    val trustedContacts by repository.trustedContactsState.collectAsState()
    val isProtectionEnabled by repository.isProtectionEnabled.collectAsState()
    val riskThreshold by repository.riskThreshold.collectAsState()

    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val bottomNavItems = listOf(
        NavRoute.Home,
        NavRoute.Calls,
        NavRoute.Trusted
    )

    var selectedCallForDetail: CallAnalysis? = null

    Scaffold(
        bottomBar = {
            if (currentRoute in bottomNavItems.map { it.route }) {
                NavigationBar(
                    containerColor = SurfaceNavy,
                    contentColor = TextPrimary,
                    tonalElevation = 8.dp
                ) {
                    bottomNavItems.forEach { item ->
                        val isSelected = currentRoute == item.route
                        NavigationBarItem(
                            selected = isSelected,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = {
                                item.icon?.let {
                                    Icon(
                                        imageVector = it,
                                        contentDescription = item.title,
                                        tint = if (isSelected) PrimaryBlue else TextSecondary
                                    )
                                }
                            },
                            label = {
                                item.title?.let {
                                    Text(
                                        text = it,
                                        color = if (isSelected) PrimaryBlue else TextSecondary,
                                        fontSize = 11.sp
                                    )
                                }
                            },
                            colors = NavigationBarItemDefaults.colors(
                                indicatorColor = CardSurface
                            )
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = NavRoute.Landing.route,
            modifier = Modifier
                .background(BackgroundNavy)
                .padding(innerPadding)
        ) {
            composable(NavRoute.Landing.route) {
                LandingScreen(
                    onGetStarted = {
                        navController.navigate(NavRoute.Home.route) {
                            popUpTo(NavRoute.Landing.route) { inclusive = true }
                        }
                    }
                )
            }

            composable(NavRoute.Home.route) {
                HomeScreen(
                    recentCalls = recentCalls,
                    isProtected = isProtectionEnabled,
                    onStartSimulation = {
                        repository.startLiveCallSimulation()
                        navController.navigate(NavRoute.LiveCall.route)
                    },
                    onOpenSettings = {
                        navController.navigate(NavRoute.Settings.route)
                    },
                    onSelectCall = { call ->
                        selectedCallForDetail = call
                        navController.navigate(NavRoute.CallResult.route)
                    }
                )
            }

            composable(NavRoute.Calls.route) {
                CallHistoryScreen(
                    calls = recentCalls,
                    onSelectCall = { call ->
                        selectedCallForDetail = call
                        navController.navigate(NavRoute.CallResult.route)
                    }
                )
            }

            composable(NavRoute.Trusted.route) {
                TrustedContactsScreen(
                    trustedContacts = trustedContacts,
                    onAddContact = { navController.navigate(NavRoute.AddTrustedContact.route) },
                    onDeleteContact = { contactId -> repository.removeTrustedContact(contactId) }
                )
            }

            composable(NavRoute.LiveCall.route) {
                LiveCallScreen(
                    liveCall = liveCallState,
                    onNavigateBack = {
                        repository.resetSimulation()
                        navController.popBackStack()
                    },
                    onVerifyCaller = {
                        navController.navigate(NavRoute.Verification.route)
                    },
                    onTriggerRiskAlert = {
                        navController.navigate(NavRoute.RiskAlert.route)
                    },
                    onEndCall = {
                        repository.stopLiveCallSimulation()
                        navController.popBackStack()
                    }
                )
            }

            composable(NavRoute.RiskAlert.route) {
                RiskAlertScreen(
                    score = liveCallState?.overallRiskScore ?: 87,
                    callerName = liveCallState?.callerName ?: "Unknown Caller",
                    onEndCall = {
                        repository.stopLiveCallSimulation()
                        navController.navigate(NavRoute.Home.route) {
                            popUpTo(NavRoute.Home.route) { inclusive = true }
                        }
                    },
                    onVerifyCaller = {
                        navController.navigate(NavRoute.Verification.route)
                    },
                    onDismiss = {
                        navController.popBackStack()
                    }
                )
            }

            composable(NavRoute.Verification.route) {
                val currentClaimed = liveCallState?.claimedIdentity ?: "Brother"
                val matchedContact = trustedContacts.find { it.relationship.equals(currentClaimed, ignoreCase = true) }

                VerificationScreen(
                    claimedIdentity = currentClaimed,
                    trustedContact = matchedContact,
                    onNavigateBack = { navController.popBackStack() },
                    onEndCall = {
                        repository.stopLiveCallSimulation()
                        navController.navigate(NavRoute.Home.route) {
                            popUpTo(NavRoute.Home.route) { inclusive = true }
                        }
                    },
                    onManualCall = { phone ->
                        // Manual call trigger
                    },
                    onMarkVerified = {
                        repository.stopLiveCallSimulation()
                        navController.navigate(NavRoute.Home.route) {
                            popUpTo(NavRoute.Home.route) { inclusive = true }
                        }
                    }
                )
            }

            composable(NavRoute.CallResult.route) {
                val callToDisplay = selectedCallForDetail ?: recentCalls.firstOrNull() ?: CallAnalysis(
                    callId = "demo_res",
                    callerName = "Unknown Caller",
                    callerNumber = "+91 98765 99999",
                    overallRiskScore = 87
                )

                CallResultScreen(
                    call = callToDisplay,
                    onNavigateBack = { navController.popBackStack() }
                )
            }

            composable(NavRoute.AddTrustedContact.route) {
                AddTrustedContactScreen(
                    onNavigateBack = { navController.popBackStack() },
                    onSaveContact = { contact ->
                        repository.addTrustedContact(contact)
                        navController.popBackStack()
                    }
                )
            }

            composable(NavRoute.Settings.route) {
                SettingsScreen(
                    isProtectionEnabled = isProtectionEnabled,
                    riskThreshold = riskThreshold,
                    onToggleProtection = { repository.setProtectionEnabled(it) },
                    onChangeThreshold = { repository.setRiskThreshold(it) },
                    onNavigateBack = { navController.popBackStack() }
                )
            }
        }
    }
}
