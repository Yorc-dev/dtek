from unittest.mock import MagicMock, patch

from django.test import TestCase


class ApplicationSerializerAuthorTest(TestCase):
    """Unit tests for auto-setting author on Application create."""

    def _make_request(self, user):
        request = MagicMock()
        request.user = user
        return request

    def _make_django_user(self):
        user = MagicMock()
        user.is_staff = True
        # Django User does NOT have 'inn'
        del user.inn
        return user

    def _make_org_user(self):
        org = MagicMock()
        org.inn = '12345678901234'
        # Organization does NOT have 'is_staff'
        del org.is_staff
        return org

    def test_author_set_to_django_user_on_create(self):
        """When request.user is a Django User with is_staff=True, author is set to that user."""
        from apps.application.serializer import ApplicationSerializer

        django_user = self._make_django_user()
        request = self._make_request(django_user)

        serializer = ApplicationSerializer(context={'request': request})
        validated_data = {}
        with patch('apps.application.serializer.serializers.ModelSerializer.create') as mock_super_create:
            mock_super_create.return_value = MagicMock()
            serializer.create(validated_data)
            self.assertEqual(validated_data.get('author'), django_user)

    def test_author_not_set_for_non_staff_user(self):
        """When request.user is a Django User with is_staff=False, author is not set."""
        from apps.application.serializer import ApplicationSerializer

        user = MagicMock()
        user.is_staff = False
        del user.inn
        request = self._make_request(user)

        serializer = ApplicationSerializer(context={'request': request})
        validated_data = {}
        with patch('apps.application.serializer.serializers.ModelSerializer.create') as mock_super_create:
            mock_super_create.return_value = MagicMock()
            serializer.create(validated_data)
            self.assertNotIn('author', validated_data)

    def test_author_not_set_for_org_user_on_create(self):
        """When request.user is an Organization, author is None (not set)."""
        from apps.application.serializer import ApplicationSerializer

        org_user = self._make_org_user()
        request = self._make_request(org_user)

        serializer = ApplicationSerializer(context={'request': request})
        validated_data = {}
        with patch('apps.application.serializer.serializers.ModelSerializer.create') as mock_super_create:
            mock_super_create.return_value = MagicMock()
            serializer.create(validated_data)
            self.assertNotIn('author', validated_data)

    def test_author_id_is_read_only_in_serializer(self):
        """author_id field must be read-only so clients cannot supply it."""
        from apps.application.serializer import ApplicationSerializer

        serializer = ApplicationSerializer()
        self.assertIn('author_id', serializer.fields)
        self.assertTrue(serializer.fields['author_id'].read_only)


class PeriodicTasksEnqueueTest(TestCase):
    """Unit tests for periodic enqueue tasks."""

    @patch('core.tasks.send_application_docx_task')
    def test_enqueue_applications_without_sedo_code(self, mock_task):
        """enqueue_applications_without_sedo_code calls .delay for each app without sedo_code."""
        from core.tasks import enqueue_applications_without_sedo_code
        from apps.application.models import Application

        mock_qs = MagicMock()
        mock_qs.values_list.return_value.iterator.return_value = iter([1, 2, 3])
        with patch.object(Application.objects, 'filter', return_value=mock_qs):
            enqueue_applications_without_sedo_code()

        self.assertEqual(mock_task.delay.call_count, 3)
        mock_task.delay.assert_any_call(1)
        mock_task.delay.assert_any_call(2)
        mock_task.delay.assert_any_call(3)

    @patch('core.tasks.generate_license_document_task')
    def test_enqueue_licenses_without_document(self, mock_task):
        """enqueue_licenses_without_document calls .delay for each license without document."""
        from core.tasks import enqueue_licenses_without_document
        from apps.license_template.models import License

        mock_qs = MagicMock()
        mock_qs.values_list.return_value.iterator.return_value = iter([10, 20])
        with patch.object(License.objects, 'filter', return_value=mock_qs):
            enqueue_licenses_without_document()

        self.assertEqual(mock_task.delay.call_count, 2)
        mock_task.delay.assert_any_call(10)
        mock_task.delay.assert_any_call(20)

