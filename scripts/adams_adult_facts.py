"""Scripture facts selected with A. Dana Adams's Bible quiz book as a guide.

The 1932 edition was copyright-renewed, so these are newly worded questions
derived from the cited KJV passages, not transcriptions of the book's prose.
"""

SOURCE_GUIDE_URL = "https://archive.org/details/4000questionsans00adam"

# difficulty, category, reference, question, correct, three distractors,
# evidence fragments that must occur in the cited KJV passage
ADAMS_ADULT_FACTS = (
    (
        "Deacon", "Moses & the Exodus", "Numbers 11:16",
        "How many elders did God tell Moses to gather to help carry Israel's leadership burden?",
        "Seventy elders", ("Twelve tribal leaders", "Twenty-four priests", "Joshua and Caleb"),
        ("seventy men of the elders of Israel",),
    ),
    (
        "Deacon", "Moses & the Exodus", "Numbers 17:8",
        "Whose staff sprouted, blossomed, and produced almonds as God's sign of the chosen priesthood?",
        "Aaron's staff", ("Moses's staff", "Joshua's staff", "Eleazar's staff"),
        ("rod of Aaron", "budded", "yielded almonds"),
    ),
    (
        "Deacon", "Moses & the Exodus", "Numbers 20:25-28",
        "Who received Aaron's priestly garments on Mount Hor?",
        "Eleazar", ("Ithamar", "Phinehas", "Moses"),
        ("put them upon Eleazar his son",),
    ),
    (
        "Deacon", "Prophets", "2 Kings 14:25",
        "Which historical book names Jonah son of Amittai outside the book of Jonah?",
        "2 Kings", ("1 Chronicles", "Ezra", "Nehemiah"),
        ("Jonah", "Amittai"),
    ),
    (
        "Deacon", "Prophecy & Fulfillment", "Acts 2:16-21",
        "Which prophet did Peter identify as the source of the Pentecost prophecy?",
        "Joel", ("Amos", "Micah", "Zechariah"),
        ("spoken by the prophet Joel",),
    ),
    (
        "Deacon", "The Apostles", "Acts 18:24-26",
        "Which married couple explained God's way more fully to Apollos?",
        "Aquila and Priscilla", ("Ananias and Sapphira", "Felix and Drusilla", "Herod and Bernice"),
        ("Aquila and Priscilla", "expounded unto him the way of God more perfectly"),
    ),
    (
        "Deacon", "The Apostles", "Acts 20:9",
        "From which level did Eutychus fall while Paul was speaking at Troas?",
        "The third story", ("The second story", "The fourth story", "The rooftop"),
        ("Eutychus", "third loft"),
    ),
    (
        "Deacon", "The Apostles", "Acts 23:16-22",
        "Which relative warned Paul about the plot to ambush him?",
        "His sister's son", ("His brother", "His father", "His cousin Barnabas"),
        ("Paul's sister's son", "lying in wait"),
    ),
    (
        "Deacon", "The Apostles", "Acts 24:1",
        "What was the name of the spokesman who presented the leaders' case against Paul to Felix?",
        "Tertullus", ("Lysias", "Festus", "Ananias"),
        ("orator named Tertullus",),
    ),
    (
        "Deacon", "Life of Jesus", "Luke 2:25-26",
        "Who was promised that he would see the Lord's Christ before he died?",
        "Simeon", ("Zacharias", "Joseph", "Nicodemus"),
        ("Simeon", "not see death", "seen the Lord's Christ"),
    ),
    (
        "Pastor", "Laws & Commandments", "Numbers 15:38-40",
        "What color cord were the Israelites commanded to place on the tassels of their garments?",
        "Blue", ("Scarlet", "Purple", "White"),
        ("ribband of blue",),
    ),
    (
        "Pastor", "Food, Feasts & Offerings", "Numbers 16:36-40",
        "What became of the bronze censers used by Korah's company?",
        "They were hammered into plates to cover the altar", ("They were buried outside the camp", "They were melted into a new lampstand", "They were stored inside the ark"),
        ("censers", "broad plates for a covering of the altar"),
    ),
    (
        "Pastor", "Kings & Kingdoms", "Deuteronomy 3:11",
        "What material was used for the bedstead of Og king of Bashan?",
        "Iron", ("Cedar", "Bronze", "Stone"),
        ("Og king of Bashan", "bedstead was a bedstead of iron"),
    ),
    (
        "Pastor", "Prophecy & Fulfillment", "Jeremiah 26:18",
        "Which earlier prophet's warning about Zion did Jeremiah's defenders quote?",
        "Micah", ("Nahum", "Habakkuk", "Zephaniah"),
        ("Micah the Morasthite prophesied",),
    ),
    (
        "Pastor", "The Apostles", "Acts 19:18-19",
        "What total value does Acts assign to the magic books burned by the Ephesian believers?",
        "Fifty thousand pieces of silver", ("Thirty pieces of silver", "Ten thousand drachmas", "One hundred talents of gold"),
        ("fifty thousand pieces of silver",),
    ),
    (
        "Pastor", "The Apostles", "Acts 21:8-9",
        "How many unmarried daughters of Philip the evangelist prophesied?",
        "Four", ("Two", "Three", "Seven"),
        ("four daughters", "did prophesy"),
    ),
    (
        "Pastor", "The Apostles", "Acts 21:10-11",
        "Which prophet used Paul's belt to demonstrate how Paul would be bound in Jerusalem?",
        "Agabus", ("Silas", "Judas Barsabas", "Philip"),
        ("Agabus", "Paul's girdle", "bound his own hands and feet"),
    ),
    (
        "Pastor", "The Apostles", "Acts 24:24-26",
        "What improper motive did Felix have for repeatedly summoning Paul?",
        "He hoped Paul would offer him money", ("He wanted Paul to write a legal defense", "He hoped Paul would join his court", "He wanted Paul to debate Tertullus"),
        ("money should have been given him of Paul",),
    ),
    (
        "Pastor", "The Apostles", "Acts 27:1-2",
        "Which Macedonian from Thessalonica sailed with Paul when he departed for Rome?",
        "Aristarchus", ("Sopater", "Secundus", "Gaius"),
        ("Aristarchus", "Macedonian of Thessalonica"),
    ),
    (
        "Pastor", "Numbers & Genealogies", "Acts 27:37",
        "How many people were aboard the ship carrying Paul toward Rome?",
        "276", ("120", "153", "300"),
        ("two hundred threescore and sixteen souls",),
    ),
)
