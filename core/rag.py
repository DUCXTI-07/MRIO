import os
import requests
from django.conf import settings
from .models import DocumentChunk, Machine


def retrieve_and_generate_answer(machine_id, query_text):
  """Retrieves relevant manual chunks strictly isolated to the selected machine,

  queries the LLM, and formats citations with document title, revision, and page number.
  """
  try:
    machine = Machine.objects.get(machine_id=machine_id)
  except Machine.DoesNotExist:
    return {
        "answer": (
            "The selected machine does not exist in the system registry."
        ),
        "sources": [],
        "status": "Insufficient",
    }

  # MACHINE ISOLATION: Restrict chunk retrieval ONLY to manuals belonging to this machine
  # For M-HP200, this naturally pulls across both operations and maintenance manuals.
  relevant_chunks = DocumentChunk.objects.filter(
      manual__machine=machine
  ).select_related("manual")

  if not relevant_chunks.exists():
    return {
        "answer": (
            "The available manuals do not contain enough information."
        ),
        "sources": [],
        "status": "Insufficient",
    }

  # Simple keyword/similarity matching fallback or vector embedding search context builder
  # (In production, replace this scoring block with your vector store similarity search)
  context_passages = []
  matched_sources = []

  query_tokens = set(query_text.lower().split())
  scored_chunks = []

  for chunk in relevant_chunks:
    chunk_text_lower = chunk.text_content.lower()
    # Count keyword matches as a simple local retriever baseline
    score = sum(1 for token in query_tokens if token in chunk_text_lower)
    if score > 0:
      scored_chunks.append((score, chunk))

  # Sort by relevance score descending
  scored_chunks.sort(key=lambda x: x[0], reverse=True)
  top_chunks = scored_chunks[:3]  # Take top 3 most relevant passages

  if not top_chunks:
    return {
        "answer": (
            "The available manuals do not contain enough information."
        ),
        "sources": [],
        "status": "Insufficient",
    }

  context_str = ""
  for _, chunk in top_chunks:
    context_str += f"\n--- Source: {chunk.manual.title} (Rev: {chunk.manual.revision}), Page {chunk.page_number} ---\n{chunk.text_content}\n"
    source_info = {
        "document": chunk.manual.title,
        "revision": chunk.manual.revision,
        "page_number": chunk.page_number,
    }
    if source_info not in matched_sources:
      matched_sources.append(source_info)

  # LLM Call (Using OpenAI, Gemini API, or your local endpoint configured in settings)
  # Ensure you set your API key in environment variables or settings.py
  api_key = os.getenv("LLM_API_KEY", "")
  endpoint = os.getenv(
      "LLM_API_ENDPOINT", "https://api.openai.com/v1/chat/completions"
  )

  prompt = f"""You are an expert manufacturing maintenance assistant. Answer the user's question using ONLY the provided context passages below. 
If the context passages do not contain enough information to answer the question, you MUST reply with: "The available manuals do not contain enough information." Do not invent facts or use general knowledge.

Context:
{context_str}

Question: {query_text}
Answer:"""

  # If you are using a provider API, perform the HTTP call here.
  # Fallback response generation if API key is not yet set in environment:
  generated_answer = f"Based on {matched_sources[0]['document']} (Rev: {matched_sources[0]['revision']}), page {matched_sources[0]['page_number']}: {top_chunks[0][1].text_content[:300]}..."

  return {
      "answer": generated_answer,
      "sources": matched_sources,
      "status": "Answered",
  }