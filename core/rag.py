"""Machine-isolated retrieval and answer formatting."""

from .models import DocumentChunk, Machine


INSUFFICIENT_ANSWER = "The available manuals do not contain enough information."


def retrieve_and_generate_answer(machine_id, query_text):
    """Find relevant chunks and return an answer with manual citations."""
    machine = Machine.objects.filter(machine_id=machine_id).first()
    if machine is None:
        return {
            "answer": "The selected machine does not exist in the system registry.",
            "sources": [],
            "status": "Insufficient",
        }

    chunks = list(
        DocumentChunk.objects.filter(manual__machine=machine)
        .select_related("manual")
    )
    if not chunks:
        return {
            "answer": INSUFFICIENT_ANSWER,
            "sources": [],
            "status": "Insufficient",
        }

    query_tokens = set(query_text.lower().split())
    scored_chunks = []
    for chunk in chunks:
        text = chunk.text_content.lower()
        score = sum(token in text for token in query_tokens)
        if score:
            scored_chunks.append((score, chunk))

    top_chunks = sorted(
        scored_chunks, key=lambda item: item[0], reverse=True
    )[:3]
    if not top_chunks:
        return {
            "answer": INSUFFICIENT_ANSWER,
            "sources": [],
            "status": "Insufficient",
        }

    sources = []
    for _, chunk in top_chunks:
        source = {
            "document": chunk.manual.title,
            "revision": chunk.manual.revision,
            "page_number": chunk.page_number,
        }
        if source not in sources:
            sources.append(source)

    best_chunk = top_chunks[0][1]
    answer = (
        f"Based on {best_chunk.manual.title} "
        f"(Rev: {best_chunk.manual.revision}), "
        f"page {best_chunk.page_number}: "
        f"{best_chunk.text_content[:300]}..."
    )
    return {"answer": answer, "sources": sources, "status": "Answered"}
