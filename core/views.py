import os
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from google import genai
from .models import Machine, DocumentChunk, QuestionRecord


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def engineer_query_view(request):
  """Handles engineer queries using RAG context and the Gemini API."""
  data = request.data
  machine_id = data.get('machine_id')
  user_question = data.get('question')

  if not machine_id or not user_question:
    return JsonResponse(
        {'error': 'machine_id and question are required.'}, status=400
    )

  try:
    machine = Machine.objects.get(machine_id=machine_id)
  except Machine.DoesNotExist:
    return JsonResponse({'error': 'Machine not found.'}, status=404)

  # 1. Retrieve relevant document chunks for this specific machine (Machine-Isolated RAG)
  # Simple keyword/text matching or vector similarity can be used here
  chunks = DocumentChunk.objects.filter(manual__machine=machine)[:5]
  context_text = '\n\n'.join([chunk.content for chunk in chunks])

  if not context_text:
    context_text = 'No manuals currently uploaded for this machine.'

  # 2. Initialize Gemini API Client
  # Ensure GEMINI_API_KEY is set in your environment variables
  client = genai.Client()

  # 3. Construct the RAG Prompt
  prompt = f"""
    You are an expert industrial maintenance assistant. Answer the engineer's question accurately 
    using ONLY the provided manual context below. If the answer is not in the context, state that 
    the manual does not contain this information. Always cite page numbers or sections if available.

    ---
    MANUAL CONTEXT:
    {context_text}
    ---

    EQUIPMENT: {machine.name} ({machine.machine_id})
    ENGINEER QUESTION: {user_question}
    """

  # 4. Generate response from Gemini
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=prompt,
  )

  answer_text = response.text

  # 5. Log the query for supervisor audit history
  QuestionRecord.objects.create(
      user=request.user,
      machine=machine,
      question=user_question,
      answer=answer_text,
  )

  return JsonResponse({
      'machine': machine.name,
      'question': user_question,
      'answer': answer_text,
      'citations_used': len(chunks),
  })