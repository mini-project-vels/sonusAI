package com.vocashield.network

object NetworkModule {
    val apiService: ApiService by lazy {
        MockApiService()
    }

}
