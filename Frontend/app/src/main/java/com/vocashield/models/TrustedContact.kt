package com.vocashield.models

data class TrustedContact(
    val id: String,
    val name: String,
    val relationship: String,
    val phoneNumber: String,
    val verificationQuestion: String,
    val expectedAnswer: String = "",
    val isVerified: Boolean = true
)
