from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()


# Message format coming from user/assistant
class Message(BaseModel):
    role: str
    content: str


# Request format for /chat
class ChatRequest(BaseModel):
    messages: List[Message]


# Load SHL catalog from catalog.json
def load_catalog():
    with open("catalog.json", "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "SHL Assessment Recommender API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    catalog = load_catalog()

    # Combine all user messages
    user_text = " ".join(
        message.content.lower()
        for message in request.messages
        if message.role == "user"
    )

    # Compare two assessments if user asks comparison
    if "compare" in user_text or "difference" in user_text:
        matched_items = []

        for item in catalog:
            item_name = item.get("name", "").lower()
            keywords = item.get("keywords", [])

            if any(keyword.lower() in user_text for keyword in keywords) or item_name in user_text:
                matched_items.append(item)

        if len(matched_items) >= 2:
            first = matched_items[0]
            second = matched_items[1]

            return {
                "reply": (
                    f"{first['name']} focuses on {first['description']} "
                    f"It has test type {first['test_type']} and duration {first.get('duration', 'not available')} minutes. "
                    f"{second['name']} focuses on {second['description']} "
                    f"It has test type {second['test_type']} and duration {second.get('duration', 'not available')} minutes."
                ),
                "recommendations": [],
                "end_of_conversation": False
            }

        return {
            "reply": "Please mention two SHL assessments or skills you want to compare, for example Python and SQL.",
            "recommendations": [],
            "end_of_conversation": False
        }
    # Off-topic questions should be refused
    off_topic_words = [
        "salary", "resume", "cv", "legal", "hack", "weather",
        "interview tips", "job apply", "cover letter"
    ]

    if any(word in user_text for word in off_topic_words):
        return {
            "reply": "I can only help with SHL assessment recommendations from the product catalog.",
            "recommendations": [],
            "end_of_conversation": False
        }

    # Skills currently available in our catalog
    skill_words = [
        "python", "java", "sql", "javascript", "hibernate",
        "java 8", "core java", "advanced java", "design patterns"
    ]


    # If user asks vague question without skill
    if not any(skill in user_text for skill in skill_words):
        return {
            "reply": "Sure. What role or skill do you want to assess? For example: Python, Java, SQL, JavaScript, or Hibernate.",
            "recommendations": [],
            "end_of_conversation": False
        }

    scored_items = []

    # These words are too general, so we do not give score for them
    common_words = [
        "developer", "software", "programming", "coding",
        "test", "assessment", "hiring", "hire", "role", "candidate"
    ]

    for item in catalog:
        score = 0
        item_name = item.get("name", "").lower()
        keywords = item.get("keywords", [])

        for keyword in keywords:
            keyword_lower = keyword.lower()

            if keyword_lower in common_words:
                continue

            if keyword_lower in user_text:
                score += 2

        # Extra score when test name matches exact skill
        if "python" in user_text and "python" in item_name:
            score += 5

        if "sql" in user_text and "sql" in item_name:
            score += 5

        if "javascript" in user_text and "javascript" in item_name:
            score += 5

        if "hibernate" in user_text and "hibernate" in item_name:
            score += 5

        # Java handling
        if "java" in user_text:
            if "java" in item_name:
                score += 5

            # Avoid JavaScript result when user asks only Java
            if "javascript" in item_name and "javascript" not in user_text:
                score -= 5

        if score > 0:
            scored_items.append((score, item))

    # Sort best matches first
    scored_items.sort(key=lambda x: x[0], reverse=True)

    recommendations = []

    for score, item in scored_items[:10]:
        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item["test_type"]
        })

    if not recommendations:
        return {
            "reply": "I could not find a strong matching SHL assessment from the current catalog. Please give more details about the role or skill.",
            "recommendations": [],
            "end_of_conversation": False
        }

    return {
        "reply": f"Based on your requirement, I found {len(recommendations)} suitable SHL assessment(s).",
        "recommendations": recommendations,
        "end_of_conversation": True
    }