"""
agents/rag_agent.py
Vector DB search + LLM answer generation.
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm_setup import llm, retrievers, precedent_db, DOMAIN_LABELS

PRECEDENT_SCORE_THRESHOLD = 0.45

TEMPLATE = """
You are Samsung Fire & Marine Insurance's top claims adjuster and legal advisor AI agent.
Please provide clear answers to the customer's questions based on the retrieved documents below.

{context_block}

[Previous Conversation]
{conversation_history}

Customer Question: {question}

Answer Writing Guidelines:
1. Ignore any insurance content in the search results that is not related to the customer's question.
2. If [Customer Policy Information] is available, reflect the customer's coverage conditions to provide a personalized answer.
3. Refer to [Previous Conversation] to maintain context continuity.
   If there are referential words like "then", "that", "earlier", find the answer from previous conversation.
4. Explain the relevant insurance policy criteria first.
5. Strictly distinguish between these two cases:
   - Only mention precedents if the [Related Precedents/Dispute Cases] section exists in the context.
   - If that section is absent, do NOT mention any precedents at all.
6. Always soften definitive expressions:
   - "will be paid" → "may be paid"
   - "is covered" → "may be covered"
   - "is impossible" → "may be difficult"
   - "applies" → "may apply"
7. Even if some content cannot be found in the retrieved documents, do NOT use negative expressions like "not specified in the policy" or "cannot be confirmed."
   Instead, provide guidance based on what was found, and recommend contacting the customer center (1588-5114) for accurate details.
8. Do NOT start with greetings like "Hello" or "Nice to meet you."
   Do NOT address the customer by name at the start. Go straight to the point.
9. Always respond in English regardless of the language of the retrieved documents.
   The policy documents may be in Korean, but your answer must be in English.

Final Answer:
"""

# ==========================================
# Query translation prompt (strict)
# ==========================================
TRANSLATE_PROMPT = """Translate the following insurance query to Korean.
Output ONLY the Korean translation. Do not add, remove, or change any meaning.
Do not add words that do not appear in the original (e.g. do not add 면책, 거절, 불가 unless they appear in the original).
If the query is already in Korean, output it as-is.

Query: {query}
Korean:"""


def translate_to_korean(text: str) -> str:
    """Translate query to Korean for vector DB search accuracy."""
    try:
        prompt = PromptTemplate.from_template(TRANSLATE_PROMPT)
        chain  = prompt | llm | StrOutputParser()
        result = chain.invoke({"query": text})
        return result.strip()
    except Exception:
        return text  # 번역 실패 시 원본 사용


def format_docs(docs, domain_label: str) -> str:
    if not docs:
        return ""
    content = "\n\n".join(doc.page_content for doc in docs)
    return f"[{domain_label} Search Results]\n{content}"


def search_and_answer(
    query: str,
    domains: list,
    customer_context: str = "",
    conversation_history: str = "",
    riders: str = ""
) -> str:
    context_blocks = []

    if customer_context:
        context_blocks.append(f"[Customer Policy Information]\n{customer_context}")

    rider_list = [r.strip() for r in riders.split(";") if r.strip()] if riders else []

    # 1. 한국어 번역 쿼리 생성 (DB가 한국어라 검색 정확도 향상)
    korean_query = translate_to_korean(query)
    print(f"  🌐 Query translated: '{query}' → '{korean_query}'")

    # 2. 검색 쿼리 구성
    search_query_kr = korean_query
    search_query_en = query
    if riders:
        search_query_kr = f"{korean_query}\n관련 특약: {riders}"
        search_query_en = f"{query}\nRelated riders: {riders}"

    for domain in domains:
        if domain == "precedent":
            continue
        if domain not in retrievers:
            continue

        # 한국어 번역 쿼리로 검색 (주 검색)
        docs = retrievers[domain].invoke(search_query_kr)
        seen = set(doc.page_content for doc in docs)

        # 원본 영어 쿼리로도 검색 (번역 환각 보완)
        for doc in retrievers[domain].invoke(search_query_en):
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                docs.append(doc)

        # 특약명별 개별 검색 (최대 3개)
        for rider in rider_list[:3]:
            for doc in retrievers[domain].invoke(rider):
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    docs.append(doc)

        print(f"  📄 [{domain}] {len(docs)} chunks retrieved (KR + EN + per-rider)")

        block = format_docs(docs[:8], DOMAIN_LABELS[domain])
        if block:
            context_blocks.append(block)

    # 판례 검색 (한국어 번역 쿼리 사용)
    precedent_results = precedent_db.similarity_search_with_score(korean_query, k=3)
    relevant_precedents = [
        doc for doc, score in precedent_results
        if score < PRECEDENT_SCORE_THRESHOLD
    ]
    if relevant_precedents:
        print(f"  ⚖️  {len(relevant_precedents)} relevant precedents found")
        block = format_docs(relevant_precedents, DOMAIN_LABELS["precedent"])
        context_blocks.append(block)
    else:
        print(f"  ⚖️  No relevant precedents → precedent context excluded")

    context_block = "\n\n" + ("=" * 40 + "\n\n").join(context_blocks)

    prompt = PromptTemplate.from_template(TEMPLATE)
    chain  = prompt | llm | StrOutputParser()

    return chain.invoke({
        "context_block":        context_block,
        "question":             query,
        "conversation_history": conversation_history if conversation_history else "None"
    })
