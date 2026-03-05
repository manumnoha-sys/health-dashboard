package com.manumnoha.healthbridge.fitbit

import android.net.Uri
import android.util.Base64
import com.google.gson.annotations.SerializedName
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.security.MessageDigest
import java.security.SecureRandom

private const val AUTH_HOST = "https://www.fitbit.com"
private const val API_BASE  = "https://api.fitbit.com"
const val FITBIT_REDIRECT_URI = "com.manumnoha.healthbridge://fitbit-callback"

// ── Token response ────────────────────────────────────────────────────────────

data class FitbitTokenResponse(
    @SerializedName("access_token")  val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("expires_in")    val expiresIn: Int,
)

// ── Heart-rate intraday ───────────────────────────────────────────────────────

data class FitbitHrDataset(
    @SerializedName("time")  val time: String,   // "HH:mm"
    @SerializedName("value") val value: Int,
)

data class FitbitHrIntraday(
    @SerializedName("dataset")         val dataset: List<FitbitHrDataset>,
    @SerializedName("datasetInterval") val datasetInterval: Int,
)

data class FitbitHrResponse(
    @SerializedName("activities-heart-intraday") val intraday: FitbitHrIntraday?,
)

// ── Steps intraday ────────────────────────────────────────────────────────────

data class FitbitStepsDataset(
    @SerializedName("time")  val time: String,
    @SerializedName("value") val value: Int,
)

data class FitbitStepsIntraday(
    @SerializedName("dataset")         val dataset: List<FitbitStepsDataset>,
    @SerializedName("datasetInterval") val datasetInterval: Int,
)

data class FitbitStepsResponse(
    @SerializedName("activities-steps-intraday") val intraday: FitbitStepsIntraday?,
)

// ── Retrofit interface ────────────────────────────────────────────────────────

interface FitbitApi {

    @FormUrlEncoded
    @POST("/oauth2/token")
    suspend fun exchangeCode(
        @Header("Authorization") basicAuth: String,
        @Field("code")           code: String,
        @Field("grant_type")     grantType: String = "authorization_code",
        @Field("redirect_uri")   redirectUri: String = FITBIT_REDIRECT_URI,
        @Field("code_verifier")  codeVerifier: String,
    ): FitbitTokenResponse

    @FormUrlEncoded
    @POST("/oauth2/token")
    suspend fun refreshToken(
        @Header("Authorization") basicAuth: String,
        @Field("grant_type")     grantType: String = "refresh_token",
        @Field("refresh_token")  refreshToken: String,
    ): FitbitTokenResponse

    @GET("/1/user/-/activities/heart/date/{date}/1d/1min.json")
    suspend fun getHeartRateIntraday(
        @Header("Authorization") bearer: String,
        @Path("date") date: String,
    ): FitbitHrResponse

    @GET("/1/user/-/activities/steps/date/{date}/1d/15min.json")
    suspend fun getStepsIntraday(
        @Header("Authorization") bearer: String,
        @Path("date") date: String,
    ): FitbitStepsResponse
}

// ── PKCE helpers ──────────────────────────────────────────────────────────────

object Pkce {
    fun generateVerifier(): String {
        val bytes = ByteArray(64)
        SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
    }

    fun challengeFrom(verifier: String): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray())
        return Base64.encodeToString(digest, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)
    }
}

// ── Client ────────────────────────────────────────────────────────────────────

class FitbitClient(private val clientId: String) {

    private val api: FitbitApi = Retrofit.Builder()
        .baseUrl(API_BASE)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(FitbitApi::class.java)

    // Empty secret = public/personal app (PKCE only, no client secret needed)
    private val basicAuth: String
        get() = "Basic " + Base64.encodeToString("$clientId:".toByteArray(), Base64.NO_WRAP)

    fun buildAuthUri(codeVerifier: String): Uri =
        Uri.parse("$AUTH_HOST/oauth2/authorize").buildUpon()
            .appendQueryParameter("response_type",        "code")
            .appendQueryParameter("client_id",            clientId)
            .appendQueryParameter("scope",                "activity heartrate profile")
            .appendQueryParameter("redirect_uri",         FITBIT_REDIRECT_URI)
            .appendQueryParameter("code_challenge",       Pkce.challengeFrom(codeVerifier))
            .appendQueryParameter("code_challenge_method","S256")
            .build()

    suspend fun exchangeCode(code: String, codeVerifier: String): FitbitTokenResponse =
        api.exchangeCode(basicAuth, code, codeVerifier = codeVerifier)

    suspend fun refreshToken(refreshToken: String): FitbitTokenResponse =
        api.refreshToken(basicAuth, refreshToken = refreshToken)

    suspend fun getHeartRateIntraday(accessToken: String, date: String): FitbitHrResponse =
        api.getHeartRateIntraday("Bearer $accessToken", date)

    suspend fun getStepsIntraday(accessToken: String, date: String): FitbitStepsResponse =
        api.getStepsIntraday("Bearer $accessToken", date)
}
