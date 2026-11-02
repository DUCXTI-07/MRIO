from django.contrib.auth.models import User
from django.db import models


class Machine(models.Model):
  """Stores registered equipment machines (e.g., M-HP200, M-AC90)."""

  machine_id = models.CharField(max_length=50, unique=True)
  name = models.CharField(max_length=100)
  description = models.TextField()

  def __str__(self):
    return f"{self.machine_id} - {self.name}"


class Manual(models.Model):
  """Stores official equipment manual PDFs linked to a specific machine."""

  machine = models.ForeignKey(
      Machine, on_delete=models.CASCADE, related_name="manuals"
  )
  title = models.CharField(max_length=255)
  revision = models.CharField(max_length=50)
  pdf_file = models.FileField(upload_to="manuals/")
  uploaded_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.title} (Rev: {self.revision})"


class DocumentChunk(models.Model):
  """Stores extracted text blocks bound to their specific manual and page number."""

  manual = models.ForeignKey(
      Manual, on_delete=models.CASCADE, related_name="chunks"
  )
  page_number = models.IntegerField()
  text_content = models.TextField()

  def __str__(self):
    return f"Manual: {self.manual.title} | Page: {self.page_number}"


class QuestionRecord(models.Model):
  """Persists engineer queries, generated answers, status, and source citations."""

  STATUS_CHOICES = [
      ("Answered", "Answered"),
      ("Insufficient", "Insufficient Evidence"),
  ]

  user = models.ForeignKey(User, on_delete=models.CASCADE)
  machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
  query = models.TextField()
  answer = models.TextField()
  sources = (
      models.JSONField()
  )  # Stores document title, revision, and page numbers
  status = models.CharField(max_length=20, choices=STATUS_CHOICES)
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"[{self.status}] {self.query[:50]}..."