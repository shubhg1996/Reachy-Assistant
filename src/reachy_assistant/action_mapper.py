"""Maps LLM response sentiment to a Reachy Mini recorded emotion or motion."""


class ActionMapper:
    """Maps LLM response sentiment to a Reachy Mini recorded emotion or motion."""

    # Emotion categories based on available library (from user's list)
    EMOTION_MAP = {
        # Positive / joyful
        "happy": [
            "cheerful1",
            "enthusiastic1",
            "enthusiastic2",
            "laughing1",
            "laughing2",
            "proud1",
            "proud2",
            "proud3",
            "success1",
            "success2",
            "dance1",
            "dance2",
            "dance3",
            "welcoming1",
            "welcoming2",
        ],
        # Sad / down
        "sad": [
            "sad1",
            "sad2",
            "downcast1",
            "lonely1",
            "exhausted1",
            "tired1",
            "resigned1",
            "lost1",
            "dying1",
        ],
        # Surprised / amazed
        "surprised": ["surprised1", "surprised2", "amazed1", "oops1", "oops2"],
        # Fear / anxiety
        "fear": ["fear1", "scared1", "anxiety1"],
        # Anger / irritation
        "anger": [
            "rage1",
            "furious1",
            "irritated1",
            "irritated2",
            "frustrated1",
            "displeased1",
            "displeased2",
            "reprimand1",
            "reprimand2",
            "reprimand3",
        ],
        # Disgust
        "disgust": ["disgusted1", "contempt1"],
        # Confusion / uncertainty
        "confused": ["confused1", "uncertain1", "incomprehensible2"],
        # Love / affection
        "love": ["loving1", "grateful1", "calming1", "serenity1"],
        # Boredom / tired
        "bored": ["boredom1", "boredom2", "sleep1"],
        # Curiosity / inquiry
        "curious": [
            "curious1",
            "inquiring1",
            "inquiring2",
            "inquiring3",
            "attentive1",
            "attentive2",
            "understanding1",
            "understanding2",
            "thoughtful1",
            "thoughtful2",
        ],
        # Yes / agreement
        "yes": ["yes1", "yes_sad1", "come1"],
        # No / disagreement
        "no": ["no1", "no_sad1", "no_excited1", "go_away1"],
        # Neutral / default (used when no keyword matches)
        "neutral": [
            "indifferent1",
            "uncomfortable1",
            "electric1",
            "relief1",
            "relief2",
            "impatient1",
            "impatient2",
            "helpful1",
            "helpful2",
            "shy1",
        ],
    }

    def __init__(self, robot):
        """Initialize the ActionMapper with a reference to the robot."""
        self.robot = robot
        # Keep track of last emotion to avoid repetition (optional)
        self.last_emotion = None

    def execute(self, llm_response):
        """Play a recorded emotion based on keywords in the LLM response."""
        text = llm_response.lower()
        emotion = self._select_emotion(text)
        print(f"Selected emotion: {emotion}")
        self.robot.moves.play_move(emotion)

    def _select_emotion(self, text):
        """Choose the most appropriate emotion from the library."""
        # Score each emotion category
        scores = {}
        for category, emotion_list in self.EMOTION_MAP.items():
            # Count keyword matches for this category
            # For simplicity, we match category name itself or common synonyms
            keywords = [category]
            if category == "happy":
                keywords = [
                    "happy",
                    "joy",
                    "glad",
                    "delighted",
                    "great",
                    "awesome",
                    "fantastic",
                    "excellent",
                ]
            elif category == "sad":
                keywords = [
                    "sad",
                    "unhappy",
                    "sorry",
                    "unfortunately",
                    "disappointed",
                    "depressed",
                    "blue",
                ]
            elif category == "surprised":
                keywords = ["surprised", "wow", "oh", "really", "amazing", "unexpected"]
            elif category == "fear":
                keywords = ["fear", "scared", "afraid", "terrified", "anxious"]
            elif category == "anger":
                keywords = [
                    "angry",
                    "mad",
                    "furious",
                    "irritated",
                    "annoyed",
                    "frustrated",
                ]
            elif category == "disgust":
                keywords = ["disgust", "gross", "yuck", "horrible"]
            elif category == "confused":
                keywords = ["confused", "what", "huh", "uncertain", "puzzled"]
            elif category == "love":
                keywords = ["love", "like", "appreciate", "thank", "grateful", "sweet"]
            elif category == "bored":
                keywords = ["bored", "tired", "sleepy", "yawn"]
            elif category == "curious":
                keywords = [
                    "curious",
                    "wonder",
                    "ask",
                    "question",
                    "tell me",
                    "explain",
                ]
            elif category == "yes":
                keywords = ["yes", "yeah", "yep", "sure", "okay", "agreed", "correct"]
            elif category == "no":
                keywords = ["no", "nope", "nah", "not", "cannot", "wrong", "incorrect"]
            else:  # neutral
                keywords = []

            score = sum(1 for kw in keywords if kw in text)
            scores[category] = score

        # Select category with highest score; if tie, pick first among ties
        best_category = max(scores, key=lambda c: scores[c])
        if scores[best_category] == 0:
            best_category = "neutral"

        # Choose an emotion from that category (prefer not repeating last one)
        emotion_list = self.EMOTION_MAP.get(best_category, self.EMOTION_MAP["neutral"])
        if self.last_emotion in emotion_list and len(emotion_list) > 1:
            # Pick a different one
            emotion = next(e for e in emotion_list if e != self.last_emotion)
        else:
            emotion = emotion_list[0]  # first in list
        self.last_emotion = emotion
        return emotion
