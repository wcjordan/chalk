"""
Tests for todos module
"""
import random
import string

from django.test import TestCase
from django.contrib.auth import get_user_model

DEFAULT_LABELS = [
    'low-energy',
    'high-energy',
    'vague',
    'work',
    'home',
    'errand',
    'mobile',
    'desktop',
    'email',
    'urgent',
    '5 minutes',
    '25 minutes',
    '60 minutes',
]


class AnyArg():  # pylint: disable=R0903
    """
    Arg matcher which matches everything
    """

    def __eq__(self, other):
        return True


def _generate_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def _stub_todo_matcher(description, labels):
    return {
        'id': AnyArg(),
        'description': description,
        'archived': False,
        'archived_at': AnyArg(),
        'completed': False,
        'completed_at': AnyArg(),
        'created_at': AnyArg(),
        'labels': labels,
    }


def _stub_label_matcher(name):
    return {
        'id': AnyArg(),
        'name': name,
    }


class ServiceTests(TestCase):
    """
    Tests for todo view
    """
    maxDiff = None

    def setUp(self):
        test_username = 'tester@localhost'
        user_model = get_user_model()
        user = user_model.objects.create(username=test_username)
        self.client.force_login(user)

    def test_todos_api(self):
        """
        Basic test which creates, updates, & deletes todos
        and fetches them to ensure they're persisted.
        """
        todo_description1 = _generate_random_string()
        labels1 = ['desktop', 'home']
        todo_description2 = _generate_random_string()
        labels2 = ['work']

        # Create a todo
        todo1_id = self._create_todo({
            'description': todo_description1,
            'labels': labels1,
        })['id']

        # Create another todo
        self._create_todo({
            'description': todo_description2,
            'labels': labels2,
        })

        # Fetch todos and verify they match expectations
        fetched_data = self._fetch_todos()
        expected_data = [
            _stub_todo_matcher(todo_description1, labels1),
            _stub_todo_matcher(todo_description2, labels2),
        ]
        self.assertCountEqual(fetched_data, expected_data)

        # Update first todo
        patch = {
            'description': _generate_random_string(),
            'labels': ['urgent'],
        }
        self._update_todo(todo1_id, patch)

        # Fetch todos and verify they match expectations
        # Expect created_at to be unchanged
        expected_data[0]['created_at'] = fetched_data[0]['created_at']
        expected_data[1]['created_at'] = fetched_data[1]['created_at']
        expected_data[0].update(patch)
        fetched_data = self._fetch_todos()
        self.assertCountEqual(fetched_data, expected_data)

        # Delete first todo
        self._delete_todo(todo1_id)

        # Fetch todos and verify they match expectations
        expected_data = [expected_data[1]]
        fetched_data = self._fetch_todos()
        self.assertCountEqual(fetched_data, expected_data)

    def test_labels_api(self):
        """
        Basic test which creates, updates, & deletes labels
        and fetches them to ensure they're persisted.
        """
        new_label = _generate_random_string()

        # Fetch and verify expectations
        fetched_data = self._fetch_labels()
        expected_data = [_stub_label_matcher(label) for label in DEFAULT_LABELS]
        self.assertCountEqual(fetched_data, expected_data)

        # Create
        label_id = self._create_label({
            'name': new_label,
        })['id']

        # Fetch and verify expectations
        fetched_data = self._fetch_labels()
        expected_data.append(_stub_label_matcher(new_label))
        self.assertCountEqual(fetched_data, expected_data)

        # Update label
        patch = {
            'name': _generate_random_string(),
        }
        self._update_label(label_id, patch)

        # Fetch and verify expectations
        expected_data[-1].update(patch)
        fetched_data = self._fetch_labels()
        self.assertCountEqual(fetched_data, expected_data)

        # Delete label
        self._delete_label(label_id)

        # Fetch and verify expectations
        expected_data = [_stub_label_matcher(label) for label in DEFAULT_LABELS]
        fetched_data = self._fetch_labels()
        self.assertCountEqual(fetched_data, expected_data)

    def _create_todo(self, data):
        return self._create_entity(data, 'todos')

    def _fetch_todos(self):
        return self._fetch_entity('todos')

    def _update_todo(self, entry_id, patch):
        return self._update_entity(entry_id, patch, 'todos')

    def _delete_todo(self, entry_id):
        return self._delete_entity(entry_id, 'todos')

    def _create_label(self, data):
        return self._create_entity(data, 'labels')

    def _fetch_labels(self):
        return self._fetch_entity('labels')

    def _update_label(self, entry_id, patch):
        return self._update_entity(entry_id, patch, 'labels')

    def _delete_label(self, entry_id):
        return self._delete_entity(entry_id, 'labels')

    def _create_entity(self, data, route):
        response = self.client.post(f'/api/todos/{route}/',
                                    data,
                                    content_type='application/json')
        self._assert_status_code(201, response)
        return response.json()

    def _fetch_entity(self, route):
        response = self.client.get(f'/api/todos/{route}/')
        self._assert_status_code(200, response)
        return response.json()

    def _update_entity(self, entry_id, patch, route):
        response = self.client.patch(f'/api/todos/{route}/{entry_id}/',
                                     patch,
                                     content_type='application/json')
        self._assert_status_code(200, response)
        return response.json()

    def _delete_entity(self, entry_id, route):
        response = self.client.delete(f'/api/todos/{route}/{entry_id}/')
        self._assert_status_code(204, response)

    def _assert_status_code(self, expected_code, response):
        self.assertEqual(
            response.status_code, expected_code,
            (f'Expected status {expected_code}, '
             f'received {response.status_code}. {response.content}'))
