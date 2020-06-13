"""
Tests for todos module
"""
import random
import string

from django.test import TestCase


class AnyArg():  # pylint: disable=R0903
    """
    Arg matcher which matches everything
    """

    def __eq__(self, other):
        return True


def _generate_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


class ServiceTests(TestCase):
    """
    Tests for todo view
    """

    def test_todos_api(self):
        """
        Basic test which creates, updates, & deletes todos
        and then fetches them to ensure they're persisted.
        """
        todo_description1 = _generate_random_string()
        todo_description2 = _generate_random_string()

        # Create a todo
        todo1_id = self._create_todo({
            'description': todo_description1,
        })['id']

        # Create another todo
        self._create_todo({
            'description': todo_description2,
        })

        # Fetch todos and verify they match expectations
        fetched_data = self._fetch_todos()
        expected_data = [{
            'id': AnyArg(),
            'description': todo_description1,
            'created_at': AnyArg(),
        }, {
            'id': AnyArg(),
            'description': todo_description2,
            'created_at': AnyArg(),
        }]
        self.assertCountEqual(fetched_data, expected_data)

        # Update first todo
        patch = {
            'description': _generate_random_string(),
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

    def _create_todo(self, data):
        return self._create_entity(data, 'todos')

    def _fetch_todos(self):
        return self._fetch_entity('todos')

    def _update_todo(self, entry_id, patch):
        return self._update_entity(entry_id, patch, 'todos')

    def _delete_todo(self, entry_id):
        return self._delete_entity(entry_id, 'todos')

    def _create_entity(self, data, route):
        response = self.client.post('/api/todos/{}/'.format(route),
                                    data,
                                    content_type='application/json')
        self._assert_status_code(201, response)
        return response.json()

    def _fetch_entity(self, route):
        response = self.client.get('/api/todos/{}/'.format(route))
        self._assert_status_code(200, response)
        return response.json()

    def _update_entity(self, entry_id, patch, route):
        response = self.client.patch('/api/todos/{}/{}/'.format(
            route, entry_id),
                                     patch,
                                     content_type='application/json')
        self._assert_status_code(200, response)
        return response.json()

    def _delete_entity(self, entry_id, route):
        response = self.client.delete('/api/todos/{}/{}/'.format(
            route, entry_id))
        self._assert_status_code(204, response)

    def _assert_status_code(self, expected_code, response):
        self.assertEqual(
            response.status_code, expected_code,
            'Expected status {}, received {}'.format(expected_code,
                                                     response.status_code))
