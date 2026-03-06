package com.manumnoha.healthbridge.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.database.ContentObserver
import android.net.Uri
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.manumnoha.healthbridge.worker.SamsungHealthSyncWorker

private const val TAG = "BridgeService"

// Candidate URIs to observe — varies by Android version and Health Connect implementation
private val HC_URIS = listOf(
    "content://com.google.android.gms.healthdata",               // GMS Health Connect (older)
    "content://com.samsung.android.service.health",              // Samsung Health direct
    "content://androidx.health.connect.client.provider.HealthConnectProvider", // Reference impl
)

class BridgeService : Service() {

    private val handler = Handler(Looper.getMainLooper())
    private val registeredObservers = mutableListOf<Pair<Uri, ContentObserver>>()

    private fun makeObserver() = object : ContentObserver(handler) {
        override fun onChange(selfChange: Boolean) {
            Log.i(TAG, "Health data changed — triggering immediate sync")
            WorkManager.getInstance(applicationContext)
                .enqueue(OneTimeWorkRequestBuilder<SamsungHealthSyncWorker>().build())
        }
    }

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIF_ID, buildNotification())
        registerObservers()
    }

    private fun registerObservers() {
        var registered = 0
        for (uriStr in HC_URIS) {
            val uri = Uri.parse(uriStr)
            val observer = makeObserver()
            runCatching {
                contentResolver.registerContentObserver(uri, true, observer)
                registeredObservers += uri to observer
                registered++
                Log.i(TAG, "Registered observer: $uriStr")
            }.onFailure {
                Log.d(TAG, "Observer not available: $uriStr")
            }
        }
        if (registered == 0) {
            Log.i(TAG, "No HC observers available — relying on periodic sync")
        }
    }

    override fun onDestroy() {
        registeredObservers.forEach { (_, obs) ->
            runCatching { contentResolver.unregisterContentObserver(obs) }
        }
        registeredObservers.clear()
        super.onDestroy()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createChannel() {
        val channel = NotificationChannel(CHANNEL_ID, "Health Bridge", NotificationManager.IMPORTANCE_LOW)
        getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
    }

    private fun buildNotification(): Notification =
        Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Health Dashboard")
            .setContentText("Syncing health data from Galaxy Watch…")
            .setSmallIcon(android.R.drawable.ic_popup_sync)
            .build()

    companion object {
        private const val NOTIF_ID = 1
        private const val CHANNEL_ID = "health_bridge"
    }
}
