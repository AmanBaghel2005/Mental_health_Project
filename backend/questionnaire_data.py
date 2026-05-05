"""
questionnaire_data.py
Structured psychological questionnaire data for 3 age groups.
Each question has: question text, type (positive/negative), category.
Scoring uses Likert scale 1-5 with type-based inversion.
"""

QUESTIONNAIRE = {
    "Child": [
        {"question": "I feel scared without knowing why", "type": "negative", "category": "emotional"},
        {"question": "I get upset very easily", "type": "negative", "category": "emotional"},
        {"question": "I enjoy playing with my friends", "type": "positive", "category": "social"},
        {"question": "I feel nervous in school", "type": "negative", "category": "school"},
        {"question": "I sleep well at night", "type": "positive", "category": "sleep"},
        {"question": "I feel like crying often", "type": "negative", "category": "emotional"},
        {"question": "I feel happy most of the time", "type": "positive", "category": "emotional"},
        {"question": "I get angry quickly", "type": "negative", "category": "emotional"},
        {"question": "I like going to school", "type": "positive", "category": "school"},
        {"question": "I feel worried about small things", "type": "negative", "category": "emotional"},
    ],

    "Youth": [
        {"question": "I feel mentally exhausted most of the time", "type": "negative", "category": "emotional"},
        {"question": "I overthink about small situations", "type": "negative", "category": "emotional"},
        {"question": "I feel anxious without a clear reason", "type": "negative", "category": "emotional"},
        {"question": "I feel calm and relaxed during the day", "type": "positive", "category": "emotional"},
        {"question": "I feel overwhelmed by my emotions", "type": "negative", "category": "emotional"},
        {"question": "I feel happy and satisfied with my life", "type": "positive", "category": "emotional"},

        {"question": "I find it hard to concentrate on studies or tasks", "type": "negative", "category": "focus"},
        {"question": "I feel motivated to achieve my goals", "type": "positive", "category": "focus"},
        {"question": "I procrastinate even when work is important", "type": "negative", "category": "focus"},
        {"question": "I can manage my time effectively", "type": "positive", "category": "focus"},
        {"question": "I feel distracted most of the time", "type": "negative", "category": "focus"},

        {"question": "I compare myself with others frequently", "type": "negative", "category": "social"},
        {"question": "I feel anxious in social situations", "type": "negative", "category": "social"},
        {"question": "I feel accepted by my friends", "type": "positive", "category": "social"},
        {"question": "I worry about what others think of me", "type": "negative", "category": "social"},
        {"question": "I feel comfortable expressing myself", "type": "positive", "category": "social"},

        {"question": "I struggle to sleep due to overthinking", "type": "negative", "category": "sleep"},
        {"question": "I feel physically tired without doing much", "type": "negative", "category": "sleep"},
        {"question": "I wake up feeling refreshed", "type": "positive", "category": "sleep"},
        {"question": "I have irregular sleep patterns", "type": "negative", "category": "sleep"},

        {"question": "I get irritated easily", "type": "negative", "category": "emotional"},
        {"question": "I feel in control of my emotions", "type": "positive", "category": "emotional"},
        {"question": "I react strongly to small problems", "type": "negative", "category": "emotional"},
        {"question": "I can handle stress effectively", "type": "positive", "category": "emotional"},

        {"question": "I feel pressure about my future or career", "type": "negative", "category": "future"},
        {"question": "I feel confident about my future", "type": "positive", "category": "future"},
        {"question": "I feel lost or unsure about what to do next", "type": "negative", "category": "future"},

        {"question": "I have lost interest in activities I used to enjoy", "type": "negative", "category": "interest"},
        {"question": "I enjoy spending time on hobbies", "type": "positive", "category": "interest"},
        {"question": "I feel bored or uninterested most of the time", "type": "negative", "category": "interest"},
    ],

    "Adult": [
        {"question": "I feel stressed due to work responsibilities", "type": "negative", "category": "work"},
        {"question": "I struggle to maintain work-life balance", "type": "negative", "category": "work"},
        {"question": "I feel overwhelmed by daily tasks", "type": "negative", "category": "work"},
        {"question": "I feel satisfied with my work", "type": "positive", "category": "work"},
        {"question": "I feel pressure to meet expectations", "type": "negative", "category": "work"},

        {"question": "I feel emotionally stable", "type": "positive", "category": "emotional"},
        {"question": "I feel anxious without a clear reason", "type": "negative", "category": "emotional"},
        {"question": "I feel frustrated or irritated frequently", "type": "negative", "category": "emotional"},
        {"question": "I feel calm and peaceful", "type": "positive", "category": "emotional"},
        {"question": "I feel mentally drained most days", "type": "negative", "category": "emotional"},

        {"question": "I have trouble sleeping or relaxing", "type": "negative", "category": "sleep"},
        {"question": "I feel physically tired even after rest", "type": "negative", "category": "sleep"},
        {"question": "I wake up feeling refreshed", "type": "positive", "category": "sleep"},
        {"question": "I experience headaches or tension due to stress", "type": "negative", "category": "sleep"},

        {"question": "I feel supported by people around me", "type": "positive", "category": "social"},
        {"question": "I feel disconnected from family or friends", "type": "negative", "category": "social"},
        {"question": "I find it hard to communicate my feelings", "type": "negative", "category": "social"},
        {"question": "I enjoy spending time with loved ones", "type": "positive", "category": "social"},

        {"question": "I worry about financial stability", "type": "negative", "category": "financial"},
        {"question": "I feel secure about my financial future", "type": "positive", "category": "financial"},
        {"question": "I feel burdened by responsibilities", "type": "negative", "category": "financial"},

        {"question": "I feel in control of my emotions", "type": "positive", "category": "emotional"},
        {"question": "I struggle to manage stress effectively", "type": "negative", "category": "emotional"},
        {"question": "I get irritated over small issues", "type": "negative", "category": "emotional"},
        {"question": "I handle difficult situations calmly", "type": "positive", "category": "emotional"},

        {"question": "I feel motivated in my daily life", "type": "positive", "category": "motivation"},
        {"question": "I feel stuck or unfulfilled in life", "type": "negative", "category": "motivation"},
        {"question": "I enjoy my daily routine", "type": "positive", "category": "motivation"},

        {"question": "I feel overwhelmed without knowing why", "type": "negative", "category": "general"},
        {"question": "I feel positive about my life overall", "type": "positive", "category": "general"},
    ],
}
