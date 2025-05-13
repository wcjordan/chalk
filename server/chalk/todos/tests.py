"""
Tests for todos module
"""
import json
import random
import string

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from chalk.todos.views import _validate_session_data, MAX_SESSION_DATA_SIZE, MAX_SESSION_KEYS

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
    'Chalk',
    'Jenkins',
    'Infra',
    'House',
    'Shopping',
    'chore',
    'up next',
    'Danyi todo',
    'Test Sheriff',
    'New Jenkins',
    'backlog',
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
        'order_rank': AnyArg(),
    }


def _stub_label_matcher(name):
    return {
        'id': AnyArg(),
        'name': name,
    }


class SessionDataValidationTests(TestCase):
    """
    Tests for session data validation
    """

    def test_valid_session_data(self):
        """Test that valid session data passes validation"""
        valid_data = {
            'environment': 'test',
            'session_guid': '123456',
            'session_data': {
                'key': 'value'
            }
        }
        data_str = json.dumps(valid_data)

        # Should not raise any exceptions
        _validate_session_data(valid_data, data_str)

    def test_invalid_data_type(self):
        """Test that non-dict data fails validation"""
        invalid_data = ['not', 'a', 'dict']
        data_str = json.dumps(invalid_data)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(invalid_data, data_str)

        self.assertIn("must be a dictionary", str(context.exception))

    def test_missing_required_keys(self):
        """Test that missing required keys fail validation"""
        # Missing environment
        missing_env = {
            'session_guid': '123456',
            'session_data': {
                'key': 'value'
            }
        }
        data_str = json.dumps(missing_env)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(missing_env, data_str)

        self.assertIn("environment", str(context.exception))

        # Missing session_guid
        missing_guid = {'environment': 'test', 'session_data': {'key': 'value'}}
        data_str = json.dumps(missing_guid)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(missing_guid, data_str)

        self.assertIn("session_guid", str(context.exception))

        # Missing session_data
        missing_data = {'environment': 'test', 'session_guid': '123456'}
        data_str = json.dumps(missing_data)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(missing_data, data_str)

        self.assertIn("session_data", str(context.exception))

    def test_too_many_keys(self):
        """Test that too many keys fail validation"""
        too_many_keys = {
            'environment': 'test',
            'session_guid': '123456',
            'session_data': {
                'key': 'value'
            },
            'extra_key': 'value'
        }
        data_str = json.dumps(too_many_keys)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(too_many_keys, data_str)

        self.assertIn(f"too many keys (max: {MAX_SESSION_KEYS})",
                      str(context.exception))

    def test_data_too_large(self):
        """Test that data exceeding size limit fails validation"""
        # Create a large string that will exceed the size limit
        large_string = "x" * (MAX_SESSION_DATA_SIZE + 1)
        large_data = {
            'environment': 'test',
            'session_guid': '123456',
            'session_data': large_string
        }
        data_str = json.dumps(large_data)

        with self.assertRaises(ValidationError) as context:
            _validate_session_data(large_data, data_str)

        self.assertIn(f"exceeds maximum size of {MAX_SESSION_DATA_SIZE}",
                      str(context.exception))


class ServiceTests(TestCase):
    """
    Tests for todo view
    """
    maxDiff = None

    def setUp(self):
        test_username = 'tester@localhost'
        user_model = get_user_model()
        user = user_model.objects.create(username=test_username)
        user.is_staff = True
        user.save()
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

    def test_reorder(self):
        """
        Test the reorder action for todos and then
        fetch todos to ensure the order is persisted.
        """
        todo_ids = [
            self._create_todo({
                'description': _generate_random_string(),
                'labels': [],
            })['id'] for _ in range(3)
        ]

        # Fetch todos and verify they match expectations
        fetched_ids = [todo['id'] for todo in self._fetch_todos()]
        self.assertCountEqual(fetched_ids, todo_ids)

        self._reorder_todo(todo_ids[2], todo_ids[0], 'after')
        reordered_ids = [todo_ids[0], todo_ids[2], todo_ids[1]]
        fetched_ids = [todo['id'] for todo in self._fetch_todos()]
        self.assertCountEqual(fetched_ids, reordered_ids)

    def test_order_rank_is_immutable(self):
        """
        Test the order rank of todos is immutable
        Try setting it on create and update calls and verify it is ignored.
        """
        todo = self._create_todo({
            'description': _generate_random_string(),
            'labels': [],
            'order_rank': 23,
        })
        assert todo['order_rank'] != 23

        todo = self._update_todo(todo['id'], {
            'order_rank': 23,
        })
        assert todo['order_rank'] != 23

    def test_status_endpoint(self):
        """
        Test the status endpoint and rebalancing
        """
        status = self._fetch_entity('status')
        assert status['closest_rank_steps'] == 45

        # Create 3 todos and shuffle them 10 times to
        # narrow the closest rank steps by 10
        todo_ids = [
            self._create_todo({
                'description': _generate_random_string(),
                'labels': [],
            })['id'] for _ in range(3)
        ]
        for step in range(10):
            move_idx = step % 2
            relative_idx = 1 - move_idx
            self._reorder_todo(todo_ids[move_idx], todo_ids[relative_idx],
                               'after')

        status = self._fetch_entity('status')
        assert status['closest_rank_steps'] == 35

        # Manually trigger an order rank rebalance
        response = self.client.post('/api/todos/rebalance_ranks/')
        self._assert_status_code(200, response)
        assert response.json() == 'Rebalanced!'

        status = self._fetch_entity('status')
        assert status['closest_rank_steps'] == 45

        # Reorder until automatic rebalance (45 - 2) steps
        for step in range(43):
            move_idx = ((step + 1) % 2) + 1
            relative_idx = 3 - move_idx
            self._reorder_todo(todo_ids[move_idx], todo_ids[relative_idx],
                               'before')

        status = self._fetch_entity('status')
        assert status['closest_rank_steps'] == 45, \
               f"Expected 45, but got {status['closest_rank_steps']}"

    def _create_todo(self, data):
        return self._create_entity(data, 'todos')

    def _fetch_todos(self):
        return self._fetch_entity('todos')

    def _update_todo(self, entry_id, patch):
        return self._update_entity(entry_id, patch, 'todos')

    def _delete_todo(self, entry_id):
        return self._delete_entity(entry_id, 'todos')

    def _reorder_todo(self, todo_id, relative_id, position):
        response = self.client.post(f'/api/todos/todos/{todo_id}/reorder/', {
            'relative_id': relative_id,
            'position': position,
        },
                                    content_type='application/json')
        self._assert_status_code(200, response)
        return response.json()

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
