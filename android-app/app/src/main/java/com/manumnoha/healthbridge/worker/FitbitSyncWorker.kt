package com.manumnoha.healthbridge.worker

import android.content.Context
import android.util.Log
import androidx.work.*
import com.manumnoha.healthbridge.BuildConfig
import com.manumnoha.healthbridge.fitbit.FitbitClient
import com.manumnoha.healthbridge.fitbit.FitbitTokenStore
import com.manumnoha.healthbridge.network.ApiClient
import com.manumnoha.healthbridge.network.WatchIngestRequest
import com.manumnoha.healthbridge.network.WatchReadingJson
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.concurrent.TimeUnit

private const val TAG = "FitbitSync"
private const val DEVICE_ID = "fitbit"

class FitbitSyncWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        if (BuildConfig.FITBIT_CLIENT_ID.isBlank()) return Result.success()

        val tokenStore = FitbitTokenStore(applicationContext)
        if (!tokenStore.hasTokens()) {
            Log.i(TAG, "No Fitbit tokens — user needs to connect via the app")
            return Result.success()
        }

        val client = FitbitClient(BuildConfig.FITBIT_CLIENT_ID)

        return try {
            // Refresh token if expired
            if (!tokenStore.isAccessTokenValid()) {
                val resp = client.refreshToken(tokenStore.refreshToken!!)
                tokenStore.saveTokens(resp.accessToken, resp.refreshToken, resp.expiresIn)
                Log.i(TAG, "Token refreshed")
            }

            val token = tokenStore.accessToken!!
            val today = LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE)

            // Use a map keyed by timestamp to merge HR + steps into the same record
            val readings = mutableMapOf<String, WatchReadingJson>()

            // Heart rate — 1-min intraday
            try {
                val hrResp = client.getHeartRateIntraday(token, today)
                hrResp.intraday?.dataset?.filter { it.value > 0 }?.forEach { s ->
                    val ts = "${today}T${s.time}:00Z"
                    readings[ts] = (readings[ts] ?: WatchReadingJson(ts))
                        .copy(heart_rate_bpm = s.value.toFloat())
                }
                Log.i(TAG, "HR samples fetched: ${hrResp.intraday?.dataset?.size ?: 0}")
            } catch (e: Exception) {
                Log.w(TAG, "HR intraday unavailable (need Personal app type on dev.fitbit.com): ${e.message}")
            }

            // Steps — 15-min intraday
            try {
                val stepsResp = client.getStepsIntraday(token, today)
                stepsResp.intraday?.dataset?.filter { it.value > 0 }?.forEach { s ->
                    val ts = "${today}T${s.time}:00Z"
                    readings[ts] = (readings[ts] ?: WatchReadingJson(ts))
                        .copy(steps_total = s.value)
                }
                Log.i(TAG, "Steps samples fetched: ${stepsResp.intraday?.dataset?.size ?: 0}")
            } catch (e: Exception) {
                Log.w(TAG, "Steps intraday failed: ${e.message}")
            }

            if (readings.isNotEmpty()) {
                val resp = ApiClient.service.ingestWatch(
                    WatchIngestRequest(DEVICE_ID, readings.values.toList())
                )
                Log.i(TAG, "Fitbit ingest: accepted=${resp.accepted} dup=${resp.duplicate_skipped}")
            }

            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Sync failed: ${e.message}")
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }

    companion object {
        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<FitbitSyncWorker>(30, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 2, TimeUnit.MINUTES)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "fitbit_sync", ExistingPeriodicWorkPolicy.KEEP, request
            )
        }
    }
}
