
# Create your tests here.
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import DocumentChunk, Machine, Manual, QuestionRecord


class ManualAssistantTests(APITestCase):

  def setUp(self):
    self.client.defaults['HTTP_X_FORWARDED_PROTO'] = 'https'

    # Create user groups for RBAC testing
    admin_group, _ = Group.objects.get_or_create(name='Administrator')
    engineer_group, _ = Group.objects.get_or_create(name='Engineer')
    supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')

    # Create test users
    self.admin_user = User.objects.create_user(
        username='admin_test', password='password123'
    )
    self.admin_user.groups.add(admin_group)

    self.engineer_user = User.objects.create_user(
        username='eng_test', password='password123'
    )
    self.engineer_user.groups.add(engineer_group)

    # Create test machine
    self.machine = Machine.objects.create(
        machine_id='M-HP200',
        name='HP-200',
        description='Test hydraulic press',
    )

  def test_machine_list_endpoint(self):
    """Test that machines can be listed publicly/anonymously or authenticated."""
    url = reverse('machine-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['machine_id'], 'M-HP200')

  def test_health_check_endpoint(self):
    """Test the deployment health endpoint."""
    response = self.client.get(reverse('health-check'))
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.json(), {'status': 'ok'})

  def test_dashboard_requires_authentication(self):
    """Test that the dashboard redirects anonymous visitors to login."""
    response = self.client.get(reverse('dashboard'))
    self.assertRedirects(
        response,
        f"{reverse('login')}?next={reverse('dashboard')}",
        fetch_redirect_response=False,
    )

  def test_engineer_query_returns_and_records_machine_isolated_answer(self):
    """Test machine-specific retrieval and query auditing."""
    manual = Manual.objects.create(
        machine=self.machine,
        title='Hydraulic Press Manual',
        revision='A',
        pdf_file='manuals/hydraulic-press.pdf',
    )
    DocumentChunk.objects.create(
        manual=manual,
        page_number=4,
        text_content='E17 indicates a hydraulic pressure fault.',
    )
    self.client.login(username='eng_test', password='password123')

    response = self.client.post(
        reverse('query-manual'),
        {
            'machine_id': self.machine.machine_id,
            'query': 'hydraulic pressure fault',
        },
        format='json',
    )

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['status'], 'Answered')
    self.assertEqual(response.data['sources'][0]['page_number'], 4)
    record = QuestionRecord.objects.get()
    self.assertEqual(record.machine, self.machine)
    self.assertEqual(record.query, 'hydraulic pressure fault')

  def test_engineer_query_unauthorized_upload(self):
    """Test that engineers cannot access admin-only manual upload endpoints."""
    self.client.login(username='eng_test', password='password123')
    url = reverse('upload-manual')
    response = self.client.post(url, {})
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)