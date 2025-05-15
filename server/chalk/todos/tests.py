"""
Tests for todos module
"""
import json
import random
import string
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from chalk.todos.consts import RANK_ORDER_DEFAULT_STEP, RANK_ORDER_INITIAL_STEP
from chalk.todos.models import RankOrderMetadata, TodoModel
from chalk.todos.signals import rebalance_rank_order
from chalk.todos.views import (_validate_session_data, MAX_SESSION_DATA_SIZE,
                               MAX_SESSION_KEYS)

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


class SignalsTests(TestCase):
    """
    Tests for signal handlers and rank order rebalancing
    """

    def setUp(self):
        # Delete all RandOrderMetadata objects to ensure a clean state
        RankOrderMetadata.objects.all().delete()

    def test_evaluate_rank_rebalance_no_trigger(self):
        """
        Test that evaluate_rank_rebalance does not trigger rebalance when
        closest_rank_steps > 2
        """
        # Create metadata with closest_rank_steps > 2
        closest_rank_steps = 3
        metadata = RankOrderMetadata.objects.create(
            closest_rank_min=0,
            closest_rank_max=2**closest_rank_steps,
            max_rank=1000)

        # Mock rebalance_rank_order to check if it's called
        with patch('chalk.todos.signals.rebalance_rank_order',
                   autospec=True) as mock_rebalance:
            # Save metadata to trigger evaluate_rank_rebalance
            metadata.save()

            # Verify rebalance was not called
            mock_rebalance.assert_not_called()

    def test_evaluate_rank_rebalance_trigger(self):
        """
        Test that evaluate_rank_rebalance triggers rebalance when
        closest_rank_steps ≤ 2
        """
        # Test cases: closest_rank_steps values
        test_cases = [2, 1, 0, None]
        for closest_rank_steps in test_cases:
            with self.subTest(closest_rank_steps=closest_rank_steps):
                # Create metadata with test case value
                metadata = RankOrderMetadata.objects.create(
                    closest_rank_min=0,
                    closest_rank_max=2**(closest_rank_steps or 0),
                    max_rank=1000)

                try:
                    # Mock rebalance_rank_order to check if it's called
                    with patch('chalk.todos.signals.rebalance_rank_order',
                               autospec=True) as mock_rebalance:
                        # Save metadata to trigger evaluate_rank_rebalance
                        metadata.save()

                        # Verify rebalance was called
                        mock_rebalance.assert_called()

                finally:
                    # Clean up for next test case
                    metadata.delete()

    def test_rebalance_rank_order(self):
        """
        Test that rebalance_rank_order correctly rebalances todos and updates
        metadata
        """
        # Create some todos with different order_ranks
        todos = []
        for i in range(5):
            todos.append(
                TodoModel.objects.create(description=f"Todo {i}", order_rank=i))

        # Create an archived todo that should be excluded from rebalancing
        archived_rank = 2
        archived_todo = TodoModel.objects.create(description="Archived Todo",
                                                 order_rank=archived_rank,
                                                 archived=True)

        # Call rebalance_rank_order
        rebalance_rank_order()

        # Verify todos were rebalanced
        last_rank = 0
        min_spacing = 2**3
        for todo in TodoModel.objects.filter(
                archived=False).order_by('order_rank'):
            self.assertGreaterEqual(
                todo.order_rank, last_rank + min_spacing,
                (f"Todo {todo.description} should have order_rank "
                 f"at least {last_rank + min_spacing}"))
            last_rank = todo.order_rank

        # Verify archived todo was not rebalanced
        archived_todo.refresh_from_db()
        self.assertEqual(archived_todo.order_rank, archived_rank,
                         "Archived todo should not be rebalanced")

        # Verify metadata was updated correctly
        metadata = RankOrderMetadata.objects.first()
        self.assertIsNotNone(metadata, "RankOrderMetadata should be created")
        self.assertEqual(metadata.closest_rank_min, RANK_ORDER_INITIAL_STEP)
        self.assertEqual(metadata.closest_rank_max,
                         RANK_ORDER_INITIAL_STEP + RANK_ORDER_DEFAULT_STEP)
        self.assertGreaterEqual(
            metadata.closest_rank_steps, min_spacing,
            "closest_rank_steps should be at least the min spacing")
        self.assertIsNotNone(metadata.last_rebalanced_at,
                             "last_rebalanced_at should be set")
        self.assertIsNotNone(metadata.last_rebalance_duration,
                             "last_rebalance_duration should be set")
        self.assertEqual(metadata.max_rank, last_rank)


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
        todo_patch = {
            'description': _generate_random_string(),
            'labels': ['urgent'],
        }
        self._update_todo(todo1_id, todo_patch)

        # Fetch todos and verify they match expectations
        # Expect created_at to be unchanged
        expected_data[0]['created_at'] = fetched_data[0]['created_at']
        expected_data[1]['created_at'] = fetched_data[1]['created_at']
        expected_data[0].update(todo_patch)
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
        todo_patch = {
            'name': _generate_random_string(),
        }
        self._update_label(label_id, todo_patch)

        # Fetch and verify expectations
        expected_data[-1].update(todo_patch)
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

    def _update_todo(self, entry_id, todo_patch):
        return self._update_entity(entry_id, todo_patch, 'todos')

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

    def _update_label(self, entry_id, label_patch):
        return self._update_entity(entry_id, label_patch, 'labels')

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

    def _update_entity(self, entry_id, entity_patch, route):
        response = self.client.patch(f'/api/todos/{route}/{entry_id}/',
                                     entity_patch,
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
