"""
agents/complaint_agent.py
Customer complaint detection + complaint CSV DB storage
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm_setup import llm

COMPLAINT_DB_PATH = Path(__file__).parent.parent / "complaint_db.csv"

CSV_HEADERS = [
    "complaint_id",
    "timestamp",
    "customer_id",
    "customer_name",
    "complaint_type",
    "sentiment_score",
    "conversation",
    "customer_query",
    "agent_response",
    "status",
]

# ==========================================
# Complaint detection prompt
# ==========================================
COMPLAINT_DETECTION_PROMPT = """
You are an insurance customer center conversation analysis AI.
Analyze the customer's statement to determine if it contains a complaint and respond in JSON only.

[Customer Statement]
{query}

[Previous Agent Response]
{response}

Respond in the following JSON format only. No other text allowed.
{{
  "is_complaint": true or false,
  "sentiment_score": number between 0-10 (0=very dissatisfied, 10=very satisfied),
  "complaint_type": "coverage dissatisfaction / claim process dissatisfaction / service dissatisfaction / policy understanding dissatisfaction / other" or null,
  "reason": "One-line summary of why it was judged as a complaint" or null
}}

Complaint detection criteria (judge as true only when clearly meeting the following conditions):
- Clear emotional complaint expressions like "unfair", "angry", "makes no sense"
- Direct protest against rejection/reduction of compensation
- Specific complaints that the process is too complicated
- Direct expression that the answer is wrong or insufficient

Must judge as false:
- Simple situation descriptions like "I did ~"
- Mentioning enrollment facts like "I enrolled in ~"
- Fact delivery like "I had an accident"
- Question-form sentences
- Sentences requesting insurance information
"""

def detect_complaint(query: str, response: str) -> dict:
    """Detect complaints from customer statements"""
    prompt = PromptTemplate.from_template(COMPLAINT_DETECTION_PROMPT)
    chain = prompt | llm | StrOutputParser()
    result_str = chain.invoke({"query": query, "response": response})
    result_str = result_str.strip().replace("```json", "").replace("```", "")
    return json.loads(result_str)


def save_complaint(
    customer_info: dict,
    query: str,
    response: str,
    detection: dict
) -> str:
    """Save complaint to CSV"""
    file_exists = COMPLAINT_DB_PATH.exists()
    with open(COMPLAINT_DB_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()

        complaint_id = f"CMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        writer.writerow({
            "complaint_id":    complaint_id,
            "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id":     customer_info.get("customer_id", ""),
            "customer_name":   customer_info.get("name", ""),
            "complaint_type":  detection.get("complaint_type", "other"),
            "sentiment_score": detection.get("sentiment_score", 0),
            "conversation":    f"Q: {query} / A: {response[:100]}...",
            "customer_query":  query,
            "agent_response":  response[:200],
            "status":          "Received",
        })

    return complaint_id


# ==========================================
# Human Handoff trigger conditions
# ==========================================
HANDOFF_KEYWORDS = [
    "FSC", "Financial Supervisory Service", "lawsuit", "legal action",
    "attorney", "lawyer", "report", "media", "news", "unfair",
    "금감원", "금융감독원", "민원", "소송", "법적조치",
    "변호사", "신고", "언론", "뉴스", "억울"
]

def check_handoff(
    customer_info: dict,
    query: str,
    answer: str,
    sentiment_score: int = None
) -> str | None:
    """
    Determine if Human Handoff is needed.
    Returns guidance message if handoff needed, None otherwise.

    Trigger conditions:
    1. Sentiment score 3 or below (strong dissatisfaction)
    2. Contains handoff keywords (FSC, lawsuit, etc.)
    3. Answer contains uncertain expressions
    """
    customer_name = customer_info.get("name", "Customer")
    reason = None

    UNCERTAIN_EXPRESSIONS = [
        "policy interpretation is ambiguous",
        "difficult to determine",
        "requires further review",
        "unclear",
        "판단하기 어렵습니다",
        "검토가 필요합니다",
    ]

    if sentiment_score is not None and sentiment_score <= 3:
        reason = "Strong dissatisfaction detected, specialist agent connection required."
    elif any(k in query for k in HANDOFF_KEYWORDS):
        reason = "Legal action or complaint-related statement detected."
    elif any(e in answer for e in UNCERTAIN_EXPRESSIONS):
        reason = "Policy interpretation is complex, specialist review required."

    if not reason:
        return None

    _save_handoff(customer_info, query, reason)
    print(f"  🚨 Human Handoff triggered | Reason: {reason}")

    return (
        f"\n\n👤 Specialist Agent Connection\n"
        f"Your inquiry exceeds AI processing scope.\n"
        f"We will connect you with a specialist agent.\n\n"
        f"📞 Specialist Agent: 1588-5114\n"
        f"🕐 Business Hours: Weekdays 09:00 ~ 18:00\n"
        f"🌐 Online Inquiry: www.samsungfire.com"
    )


def _save_handoff(customer_info: dict, query: str, reason: str):
    """Save handoff record to CSV"""
    HANDOFF_DB_PATH = Path(__file__).parent.parent / "handoff_db.csv"
    HEADERS = ["handoff_id", "timestamp", "customer_id", "customer_name", "reason", "query", "status"]

    file_exists = HANDOFF_DB_PATH.exists()
    with open(HANDOFF_DB_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "handoff_id":    f"HND-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id":   customer_info.get("customer_id", ""),
            "customer_name": customer_info.get("name", ""),
            "reason":        reason,
            "query":         query,
            "status":        "Pending",
        })


def check_and_record(
    customer_info: dict,
    query: str,
    response: str
) -> str | None:
    detection = detect_complaint(query, response)

    if not detection.get("is_complaint"):
        handoff_msg = check_handoff(customer_info, query, response)
        return handoff_msg

    complaint_id = save_complaint(customer_info, query, response, detection)
    score = detection.get("sentiment_score", 0)

    print(f"  🚨 Complaint detected | Type: {detection.get('complaint_type')} | Score: {score}/10 | ID: {complaint_id}")

    if score <= 3:
        empathy = (
            f"We fully understand your frustration. "
            f"We will forward this to our team for prompt review. "
            f"Your complaint reference number is {complaint_id}."
        )
    else:
        empathy = (
            f"We apologize for the inconvenience. "
            f"Your feedback is valuable and will be reflected in our improvements. "
            f"Your complaint reference number is {complaint_id}."
        )

    empathy_msg = f"\n\n💬 {empathy}"
    handoff_msg = check_handoff(customer_info, query, response, sentiment_score=score)

    return empathy_msg + (handoff_msg if handoff_msg else "")
