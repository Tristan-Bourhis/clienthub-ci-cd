import unittest

from app import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'status': 'ok'})

    def test_who(self):
        response = self.client.get('/who')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'Tristan Bourhis')
        self.assertEqual(response.mimetype, 'text/plain')


if __name__ == '__main__':
    unittest.main()
