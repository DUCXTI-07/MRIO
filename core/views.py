from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Manual, QuestionRecord, Machine
from .serializers import (
    ManualUploadSerializer,
    QuerySerializer,
    QuestionRecordSerializer,
    MachineSerializer,
)
from .permissions import IsAdministrator, IsEngineer, IsSupervisor
from .utils import ingest_manual_pdf
from .rag import retrieve_and_generate_answer


class ManualUploadView(APIView):
  """Administrator-only endpoint to upload and index equipment manuals."""
  permission_classes = [IsAdministrator]

  def post(self, request):
    serializer = ManualUploadSerializer(data=request.data)
    if serializer.is_valid():
      manual = serializer.save()
      ingest_manual_pdf(manual)
      return Response(
          {
              "message": (
                  "Manual uploaded, parsed, and indexed successfully."
              ),
              "manual_id": manual.id,
          },
          status=status.HTTP_201_CREATED,
      )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EngineerQueryView(APIView):
  """Engineer endpoint to submit maintenance questions with machine context."""
  permission_classes = [IsEngineer]

  def post(self, request):
    serializer = QuerySerializer(data=request.data)
    if serializer.is_valid():
      machine_id = serializer.validated_data["machine_id"]
      query_text = serializer.validated_data["query"]

      result = retrieve_and_generate_answer(machine_id, query_text)

      machine_obj = Machine.objects.get(machine_id=machine_id)
      QuestionRecord.objects.create(
          user=request.user,
          machine=machine_obj,
          query=query_text,
          answer=result["answer"],
          sources=result["sources"],
          status=result["status"],
      )

      return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupervisorHistoryView(ListAPIView):
  """Supervisor read-only endpoint to review question history and audit logs."""
  permission_classes = [IsSupervisor]
  queryset = QuestionRecord.objects.all().order_by("-timestamp")
  serializer_class = QuestionRecordSerializer


def dashboard_view(request):
  """Renders the frontend dashboard HTML template."""
  return render(request, "core/dashboard.html")


class MachineListView(ListAPIView):
  """Read-only endpoint to list all registered machines for frontend selection."""
  queryset = Machine.objects.all()
  serializer_class = MachineSerializer


class ManualListView(ListAPIView):
  """Read-only endpoint to list manuals, optionally filtered by machine_id."""
  serializer_class = ManualUploadSerializer

  def get_queryset(self):
    queryset = Manual.objects.all()
    machine_id = self.request.query_params.get("machine_id")
    if machine_id:
      queryset = queryset.filter(machine__machine_id=machine_id)
    return queryset