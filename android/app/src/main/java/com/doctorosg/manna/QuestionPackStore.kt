package com.oddcurrent.manna

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL

object QuestionPackStore {
    const val EXPECTED_QUESTION_COUNT = 10_000
    private const val FILE_NAME = "question-pack-10000-v1.json"

    fun isInstalled(context: Context): Boolean = context.getFileStreamPath(FILE_NAME).isFile

    fun loadInstalled(context: Context): List<Question> = runCatching {
        if (!isInstalled(context)) emptyList()
        else parseAndValidate(context.getFileStreamPath(FILE_NAME).readText())
    }.getOrDefault(emptyList())

    suspend fun downloadAndInstall(context: Context, remoteURL: String): List<Question> = withContext(Dispatchers.IO) {
        val connection = URL(remoteURL).openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = 15_000
            connection.readTimeout = 60_000
            connection.requestMethod = "GET"
            if (connection.responseCode !in 200..299) error("The extra question pack could not be downloaded. Please try again.")
            val text = connection.inputStream.bufferedReader().use { it.readText() }
            val questions = parseAndValidate(text)
            val destination = context.getFileStreamPath(FILE_NAME)
            val temporary = context.getFileStreamPath("$FILE_NAME.tmp")
            temporary.writeText(text)
            if (!temporary.renameTo(destination)) {
                temporary.copyTo(destination, overwrite = true)
                temporary.delete()
            }
            questions
        } finally {
            connection.disconnect()
        }
    }

    fun parseAndValidate(text: String): List<Question> {
        val array = JSONArray(text)
        require(array.length() == EXPECTED_QUESTION_COUNT) { "The downloaded question pack did not pass validation." }
        val questions = List(array.length()) { i ->
            val item = array.getJSONObject(i)
            val options = item.getJSONArray("options")
            Question(
                item.getString("id"), item.getInt("number"), item.getString("category"),
                item.getString("difficulty"), item.getString("question"),
                List(options.length()) { options.getString(it) }, item.getString("correct"),
                item.optString("explanation"),
                item.optString("ageGroup").takeIf { it.isNotBlank() && it != "null" },
                item.optString("pastorFormat").takeIf { it.isNotBlank() && it != "null" }
            )
        }
        require(questions.map { it.id }.toSet().size == questions.size &&
            questions.all { it.id.isNotBlank() && it.question.isNotBlank() && it.options.size >= 2 && it.correct in it.options }) {
            "The downloaded question pack did not pass validation."
        }
        return questions
    }
}
