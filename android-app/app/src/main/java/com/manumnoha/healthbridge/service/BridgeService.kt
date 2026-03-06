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

// Health Connect writes new data here when Samsung Health syncs from the watch
private val HC_URI: Uri = Uri.parse("content://androidx.health.connect.client.provider.HealthConnectProvider")

class BridgeService : Service() {

    private val hcObserver = object : ContentObserver(Handler(Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean) {
            Log.i(TAG, "Health Connect data changed — triggering immediate sync")
            WorkManager.getInstance(applicationContext)
                .enqueue(OneTimeWorkRequestBuilder<SamsungHealthSyncWorker>().build())
        }
    }

    override fun onCreate() {
        super.onCreate()
        createChannel()
        startForeground(NOTIF_ID, buildNotification())
        // Watch for new Health Connect data (written by Samsung Health from Galaxy Watch)
        runCatching {
            contentResolver.registerContentObserver(HC_URI, true, hcObserver)
            Log.i(TAG, "Registered Health Connect ContentObserver")
        }.onFailure {
            Log.w(TAG, "Could not register HC observer: ${it.message}")
        }
    }

    override fun onDestroy() {
        runCatching { contentResolver.unregisterContentObserver(hcObserver) }
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
