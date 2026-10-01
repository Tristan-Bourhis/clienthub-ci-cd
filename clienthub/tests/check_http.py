"""Tests d'intégration HTTP : python3 tests/check_http.py (stack démarrée)."""
import json
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen


class ClientHubTests(unittest.TestCase):
    def test_health(self):
        with urlopen("http://127.0.0.1:5000/health", timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_clients_from_database(self):
        with urlopen("http://127.0.0.1:5000/clients", timeout=10) as response:
            clients = json.load(response)
        self.assertGreaterEqual(len(clients), 3)
        self.assertTrue({"Alice Martin", "Bob Dupont", "Chloé Bernard"}.issubset(
            {client["name"] for client in clients}
        ))
        self.assertTrue(all(isinstance(client["id"], int) for client in clients))

    def test_portal(self):
        with urlopen("http://127.0.0.1:8080/", timeout=10) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("ClientHub", response.read().decode())

    def test_unknown_route(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen("http://127.0.0.1:5000/page-inconnue", timeout=10)
        self.assertEqual(raised.exception.code, 404)
        raised.exception.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
