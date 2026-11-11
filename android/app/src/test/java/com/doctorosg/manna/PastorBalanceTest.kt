package com.oddcurrent.manna

import org.junit.Assert.assertEquals
import org.junit.Test

class PastorBalanceTest {
    @Test
    fun fiveAndTenQuestionBlocksLimitRoteRecall() {
        val questions = PastorQuestionFormat.entries.flatMap { format ->
            (1..10).map { index ->
                Question(
                    id = "${format.wireValue}-$index",
                    number = index,
                    category = "Life of Jesus",
                    difficulty = "Pastor",
                    question = "Question $index",
                    options = listOf("A", "B", "C", "D"),
                    correct = "A",
                    explanation = "",
                    pastorFormat = format.wireValue
                )
            }
        }

        val balanced = balancedPastorQuestions(questions)
        val firstFive = balanced.take(5).groupingBy { it.resolvedPastorFormat() }.eachCount()
        assertEquals(1, firstFive[PastorQuestionFormat.SCRIPTURE_MEMORY])
        assertEquals(2, firstFive[PastorQuestionFormat.INTERPRETATION])
        assertEquals(1, firstFive[PastorQuestionFormat.ORIGINAL_LANGUAGE])
        assertEquals(1, firstFive[PastorQuestionFormat.OTHER])
        assertEquals(null, firstFive[PastorQuestionFormat.CHURCH_FATHER])

        val firstTen = balanced.take(10).groupingBy { it.resolvedPastorFormat() }.eachCount()
        assertEquals(2, firstTen[PastorQuestionFormat.SCRIPTURE_MEMORY])
        assertEquals(4, firstTen[PastorQuestionFormat.INTERPRETATION])
        assertEquals(2, firstTen[PastorQuestionFormat.ORIGINAL_LANGUAGE])
        assertEquals(1, firstTen[PastorQuestionFormat.OTHER])
        assertEquals(1, firstTen[PastorQuestionFormat.CHURCH_FATHER])
    }
}
