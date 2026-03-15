# -----------------------------------------------
# FAKE KNOWLEDGE BASE - Simulating RAG
# In a real system, this would be a PDF or database
# -----------------------------------------------

DOCUMENTS = [
    {
        "id": 1,
        "title": "BOT Consulting Services",
        "content": "BOT Consulting offers a wide range of services including artificial intelligence solutions, data analytics, cloud computing, and digital transformation. Our AI team specializes in building conversational AI platforms, chatbots, and enterprise automation tools."
    },
    {
        "id": 2,
        "title": "BOT Consulting Team",
        "content": "BOT Consulting has a team of over 50 engineers and consultants. The team includes AI engineers, data scientists, backend developers, and cloud architects. We work with clients across finance, healthcare, and retail industries."
    },
    {
        "id": 3,
        "title": "BOT GPT Product",
        "content": "BOT GPT is a conversational AI platform built by BOT Consulting. It supports multi-turn conversations, document grounding, and enterprise workflows. BOT GPT integrates with OpenAI, Claude, and Llama models."
    },
    {
        "id": 4,
        "title": "Pricing and Plans",
        "content": "BOT Consulting offers three pricing plans: Starter at $99 per month, Professional at $299 per month, and Enterprise with custom pricing. All plans include API access, conversation history, and basic support."
    },
    {
        "id": 5,
        "title": "Contact and Support",
        "content": "BOT Consulting is headquartered in New York. You can reach our support team at support@botconsulting.com. We offer 24/7 support for enterprise clients and business hours support for starter and professional plans."
    }
]


# -----------------------------------------------
# SIMPLE KEYWORD SEARCH
# Finds relevant document chunks for a user query
# -----------------------------------------------
def retrieve_relevant_context(query: str, top_k: int = 2) -> str:
    query_words = query.lower().split()
    
    scored_docs = []
    
    for doc in DOCUMENTS:
        content_lower = doc["content"].lower()
        # Count how many query words appear in this document
        score = sum(1 for word in query_words if word in content_lower)
        if score > 0:
            scored_docs.append((score, doc))
    
    # Sort by score - highest first
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    # Take top_k most relevant documents
    top_docs = scored_docs[:top_k]
    
    if not top_docs:
        return ""
    
    # Combine into one context string
    context = "\n\n".join([
        f"[{doc['title']}]: {doc['content']}"
        for _, doc in top_docs
    ])
    
    return context
