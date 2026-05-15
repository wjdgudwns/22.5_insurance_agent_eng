"""
agents/claim_agent.py
Insurance claim document submission + image classification + checklist verification + review status return
"""

import json
import base64
import os
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm_setup import llm

# ==========================================
# Required documents checklist by domain
# ==========================================
BASE_DOCUMENTS = {
    "auto": [
        "Accident Report Confirmation",
        "Traffic Accident Fact Confirmation",
        "Medical Certificate or Doctor's Opinion",
        "Repair Estimate or Repair Receipt",
        "Vehicle Accident Photos",
    ],
    "cancer": [
        "Insurance Claim Form (Samsung Fire & Marine format)",
        "Cancer Diagnosis Confirmation",
        "Hospital Medical Records Copy",
        "Hospitalization Confirmation (if hospitalized)",
        "Hospital Receipt",
    ],
    "teeth": [
        "Insurance Claim Form (Samsung Fire & Marine format)",
        "Dental Diagnosis Certificate",
        "Dental Medical Records Copy",
        "Dental Treatment Receipt",
    ],
}

RIDER_DOCUMENTS = {
    "렌터카특약":    ["Rental Car Usage Receipt", "Rental Car Contract"],
    "긴급출동특약":  ["Emergency Dispatch Service Confirmation"],
    "자기차량손해":  ["Repair Completion Confirmation", "Vehicle Registration Copy"],
    "대물확장특약":  ["Third Party Vehicle Repair Estimate"],
    "재진단암특약":  ["Re-diagnosed Cancer Diagnosis Confirmation"],
    "고액암특약":    ["High-cost Cancer Diagnosis Confirmation (cancer type specified)"],
    "항암치료특약":  ["Chemotherapy Confirmation", "Prescription Copy"],
    "임플란트특약":  ["Implant Procedure Confirmation", "X-ray Images"],
    "크라운특약":    ["Crown Treatment Confirmation"],
    "보철치료특약":  ["Prosthetic Treatment Confirmation"],
}

MIME_MAP = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".pdf":  "application/pdf",
}

# ==========================================
# Image document classification prompt
# ==========================================
IMAGE_CLASSIFY_PROMPT = """
You are an insurance claim document classification expert.
Look at the image below and determine what type of document it is. Respond in JSON only.
No other text is allowed.

{
  "doc_type": "medical certificate / receipt / medical records / accident photo / repair estimate / prescription / procedure confirmation / other",
  "confidence": "high / medium / low",
  "detail": "One-line summary of key information confirmed from the document"
}
"""

# ==========================================
# Document validation prompt
# ==========================================
VALIDATION_PROMPT = """
You are an insurance claim document reviewer.
Compare the customer's submitted documents with the required documents and respond in JSON only.

[Required Documents]
{required_docs}

[Customer Submitted Documents]
{submitted_docs}

Respond in the following JSON format only. No other text allowed.
{{
  "is_complete": true or false,
  "missing_docs": ["list of missing documents"],
  "valid_docs": ["list of confirmed documents"],
  "status": "accepted or missing documents",
  "message": "One-line guidance message for the customer"
}}
"""

# ==========================================
# Helper functions
# ==========================================
def get_required_docs(domain: str, riders: str) -> list:
    """Generate required documents list based on domain + riders"""
    docs = BASE_DOCUMENTS.get(domain, []).copy()
    rider_list = [r.strip() for r in riders.split(";") if r.strip()]
    for rider in rider_list:
        docs.extend(RIDER_DOCUMENTS.get(rider, []))
    return list(dict.fromkeys(docs))


def get_riders(customer_info: dict, domain: str) -> str:
    """Extract riders for the given domain from customer info"""
    product_map = {"auto": "P-C", "cancer": "P-B", "teeth": "P-D"}
    for p in customer_info.get("policies", []):
        if p.get("product_id") == product_map.get(domain):
            return p.get("riders", "")
    return ""


def validate_documents(domain: str, riders: str, submitted_docs: list) -> dict:
    """Compare submitted documents vs required documents"""
    required_docs = get_required_docs(domain, riders)
    prompt = PromptTemplate.from_template(VALIDATION_PROMPT)
    chain = prompt | llm | StrOutputParser()
    result_str = chain.invoke({
        "required_docs":  "\n".join(f"- {d}" for d in required_docs),
        "submitted_docs": "\n".join(f"- {d}" for d in submitted_docs),
    })
    result_str = result_str.strip().replace("```json", "").replace("```", "")
    return json.loads(result_str)


def format_claim_result(
    validation: dict,
    domain_en: str,
    customer_info: dict,
    query: str
) -> str:
    """Convert validation result to customer guidance string"""

    SPECIALIST_REASON = {
        "음주":     "Drunk driving accidents require review of exemption clauses.",
        "면책":     "Exemption clause applicability needs to be confirmed.",
        "고지의무": "Duty of disclosure violation needs to be confirmed.",
        "기왕증":   "Pre-existing condition applicability needs to be confirmed.",
        "분쟁":     "Dispute-related case requires specialist review.",
        "소송":     "Litigation-related case requires specialist review.",
        "자살":     "Suicide-related case requires specialist review.",
        "고의":     "Intentional accident needs to be confirmed.",
        "전쟁":     "War/natural disaster exemption needs to be confirmed.",
        "천재지변": "War/natural disaster exemption needs to be confirmed.",
        "drunk":    "Drunk driving accidents require review of exemption clauses.",
        "DUI":      "DUI accidents require review of exemption clauses.",
    }

    reason = next(
        (SPECIALIST_REASON[k] for k in SPECIALIST_REASON if k in query),
        None
    )

    # Case 1: Specialist review required
    if reason:
        return (
            f"🔍 {domain_en} - Specialist Review Required\n"
            f"Documents have been confirmed, but specialist review is required for the following reason.\n"
            f"⚠️ Reason: {reason}\n\n"
            f"📞 Specialist Consultation: 1588-5114 (Samsung Fire & Marine Customer Center)\n"
            f"⏱️ Processing Time: 5-10 business days"
        )

    # Case 2: All documents complete → Claim accepted
    if validation["is_complete"]:
        claim_number = f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        timestamp    = datetime.now().strftime("%Y-%m-%d %H:%M")
        return (
            f"✅ {domain_en} - Claim Successfully Submitted\n"
            f"Claim Number : {claim_number}\n"
            f"Submitted At : {timestamp}\n"
            f"Review Status : 🔄 Documents Under Review\n\n"
            f"Confirmed Documents:\n"
            + "\n".join(f"  ✅ {d}" for d in validation["valid_docs"]) +
            f"\n\nEstimated Processing Time: 3-5 business days\n"
            f"Results will be sent to the registered contact ({customer_info.get('phone', '')})."
        )

    # Case 3: Missing documents → Resubmission required
    else:
        return (
            f"⚠️ {domain_en} - Missing Documents Notice\n"
            f"Confirmed Documents:\n"
            + "\n".join(f"  ✅ {d}" for d in validation["valid_docs"]) +
            f"\n\nMissing Documents (Resubmission Required):\n"
            + "\n".join(f"  ❌ {d}" for d in validation["missing_docs"]) +
            f"\n\nPlease submit the missing documents to proceed with the review.\n"
            f"📞 Contact: 1588-5114 (Samsung Fire & Marine Customer Center)"
        )


# ==========================================
# Image classification
# ==========================================
def classify_document_image(image_path: str) -> dict:
    """Analyze image file using Gemini Vision and return document type"""
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash")

    ext        = Path(image_path).suffix.lower()
    mime_type  = MIME_MAP.get(ext, "image/jpeg")
    image_data = base64.b64encode(Path(image_path).read_bytes()).decode()

    response = model.generate_content([
        IMAGE_CLASSIFY_PROMPT,
        {"mime_type": mime_type, "data": image_data}
    ])

    result_str = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(result_str)


# ==========================================
# Main function
# ==========================================
def handle_claim(
    customer_info: dict,
    domain: str,
    query: str,
    submitted_docs: list = None,
    image_paths: list = None
) -> str:
    customer_name = customer_info.get("name", "Customer")
    domain_en = {
        "auto":   "Auto Insurance",
        "cancer": "Cancer Insurance",
        "teeth":  "Dental Insurance"
    }.get(domain, domain)

    riders        = get_riders(customer_info, domain)
    required_docs = get_required_docs(domain, riders)

    # Image submission
    if image_paths:
        print(f"  🖼️  Analyzing {len(image_paths)} images...")
        classified = []
        for path in image_paths:
            result = classify_document_image(path)
            classified.append(result)
            print(f"    - {Path(path).name} → {result['doc_type']} (confidence: {result['confidence']})")
        submitted_docs = [c["doc_type"] for c in classified if c["confidence"] != "low"]

    # No documents submitted: provide required documents guidance
    if not submitted_docs:
        docs_str = "\n".join(f"  {i+1}. {d}" for i, d in enumerate(required_docs))
        return (
            f"📋 {domain_en} - Claim Guidance\n"
            f"Required documents including {customer_name}'s riders ({riders}):\n\n"
            f"{docs_str}\n\n"
            f"📞 Document Submission: 1588-5114 (Samsung Fire & Marine Customer Center)\n"
            f"🌐 Online Submission: www.samsungfire.com → Insurance Claims"
        )

    # Proceed with document validation
    print(f"  📄 Validating documents... ({len(submitted_docs)} items)")
    validation = validate_documents(domain, riders, submitted_docs)

    return format_claim_result(validation, domain_en, customer_info, query=query)
