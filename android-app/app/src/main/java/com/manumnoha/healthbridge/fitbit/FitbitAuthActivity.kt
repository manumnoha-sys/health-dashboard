package com.manumnoha.healthbridge.fitbit

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import com.manumnoha.healthbridge.BuildConfig
import kotlinx.coroutines.*

private const val TAG = "FitbitAuth"

/**
 * Handles the Fitbit OAuth2 PKCE flow.
 *
 * Launched two ways:
 *  1. From MainActivity "Connect Fitbit" button — starts the auth browser flow.
 *  2. As the target of the custom-scheme redirect URI after Fitbit authorization
 *     (com.manumnoha.healthbridge://fitbit-callback?code=xxx).
 */
class FitbitAuthActivity : Activity() {

    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        val data: Uri? = intent.data
        if (data?.scheme == "com.manumnoha.healthbridge" && data.host == "fitbit-callback") {
            val code  = data.getQueryParameter("code")
            val error = data.getQueryParameter("error")
            when {
                error != null -> {
                    Log.e(TAG, "OAuth error: $error")
                    Toast.makeText(this, "Fitbit auth failed: $error", Toast.LENGTH_LONG).show()
                    finish()
                }
                code != null -> exchangeCode(code)
                else -> finish()
            }
        } else {
            startOAuth()
        }
    }

    private fun startOAuth() {
        if (BuildConfig.FITBIT_CLIENT_ID.isBlank()) {
            Toast.makeText(this, "Fitbit client ID not configured", Toast.LENGTH_LONG).show()
            finish()
            return
        }
        val tokenStore = FitbitTokenStore(this)
        val verifier = Pkce.generateVerifier()
        tokenStore.codeVerifier = verifier

        val authUri = FitbitClient(BuildConfig.FITBIT_CLIENT_ID).buildAuthUri(verifier)
        startActivity(Intent(Intent.ACTION_VIEW, authUri))
        // Stay alive so we receive the redirect in onNewIntent
    }

    private fun exchangeCode(code: String) {
        val tokenStore = FitbitTokenStore(this)
        val verifier = tokenStore.codeVerifier
        if (verifier == null) {
            Toast.makeText(this, "Auth session expired — please try again", Toast.LENGTH_LONG).show()
            finish()
            return
        }
        scope.launch {
            try {
                val resp = withContext(Dispatchers.IO) {
                    FitbitClient(BuildConfig.FITBIT_CLIENT_ID).exchangeCode(code, verifier)
                }
                tokenStore.saveTokens(resp.accessToken, resp.refreshToken, resp.expiresIn)
                tokenStore.codeVerifier = null
                Log.i(TAG, "Fitbit connected successfully")
                Toast.makeText(this@FitbitAuthActivity, "Fitbit connected!", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Log.e(TAG, "Token exchange failed: ${e.message}")
                Toast.makeText(this@FitbitAuthActivity, "Failed to connect Fitbit: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                finish()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }
}
