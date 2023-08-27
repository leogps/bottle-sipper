import unittest
import os
from sipper import Sipper


class TestApplication(unittest.TestCase):
    """Checking if command-line args work"""

    def test_directory(self):
        sipper = Sipper('/')
        self.assertEqual(sipper.directory, '/')

    def test_show_directory_listings(self):
        sipper = Sipper('/')
        self.assertEqual(sipper.show_directory_listings, True)

    def test_shutdown(self):
        sipper = Sipper('/')
        sipper.start_sipping('0.0.0.0', 8089)
        sipper.shutdown(wait_before_shutdown=2)

    def test_ssl(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cert = os.path.join(test_dir, 'test-cert', 'server.crt')
        key = os.path.join(test_dir, 'test-cert', 'server.key')

        sipper = Sipper('/', ssl_enabled=True, ssl_cert=cert, ssl_key=key)
        sipper.start_sipping('0.0.0.0', 8099)
        sipper.shutdown(wait_before_shutdown=2)

    def test_ssl_validation(self):
        with self.assertRaises(Exception):
            Sipper('/', ssl_enabled=True)

        test_dir = os.path.dirname(os.path.abspath(__file__))

        with self.assertRaises(Exception):
            cert = os.path.join(test_dir, 'test-cert', 'server.crt')
            Sipper('/', ssl_enabled=True, ssl_cert=cert)

        with self.assertRaises(Exception):
            key = os.path.join(test_dir, 'test-cert', 'server.key')
            Sipper('/', ssl_enabled=True, ssl_key=key)


if __name__ == "__main__":
    unittest.main()
