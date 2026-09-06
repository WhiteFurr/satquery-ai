import unittest

from fastapi.testclient import TestClient

from backend import app


class BackendApiTests(unittest.TestCase):
    def test_status_endpoint(self):
        client = TestClient(app)
        response = client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('request', payload)
        self.assertIn('classification', payload)

    def test_analyze_endpoint_returns_user_inputs_and_response(self):
        client = TestClient(app)
        with open('data/demo_images/satellite_1.jpg', 'rb') as image:
            response = client.post(
                '/api/analyze',
                files={'file': ('satellite_1.jpg', image, 'image/jpeg')},
                data={'mode': 'vqa', 'query': 'How many buildings are there?'}
            )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload['input']['query'], 'How many buildings are there?')
        self.assertIn('answer', payload['result'])
        self.assertIn('request', payload)


if __name__ == '__main__':
    unittest.main()
