import os
import socket
import threading
import time
import unittest
from http.client import HTTPConnection

from sipper import Sipper


def wait_for_server(address, port, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((address, port), timeout=1):
                return True  # Server is up
        except socket.error:
            time.sleep(1)  # Wait for 1 second before trying again
    return False  # Timeout reached, server not up


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
        address = '0.0.0.0'
        port = 8089
        try:
            sipper.start_sipping(address, port)

            # Wait for the server to be ready
            self.assertTrue(wait_for_server(address, port), "Server did not start in time.")
        finally:
            sipper.shutdown(wait_before_shutdown=2)
            sipper.await_sipping_complete()

    def test_ssl(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        cert = os.path.join(test_dir, 'test-cert', 'server.crt')
        key = os.path.join(test_dir, 'test-cert', 'server.key')

        address = '0.0.0.0'
        port = 8099
        sipper = Sipper('/', ssl_enabled=True, ssl_cert=cert, ssl_key=key)
        try:
            sipper.start_sipping(address, port)

            # Wait for the server to be ready
            self.assertTrue(wait_for_server(address, port), "Server did not start in time.")
        finally:
            sipper.shutdown(wait_before_shutdown=2)
            sipper.await_sipping_complete()

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

    # Wait for the server to start by polling the socket

    def test_gzip_serving(self):
        """Test that Sipper server serves gzipped file when gzip=True option is enabled"""

        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_gzip_dir = os.path.join(test_dir, 'test-gzip')
        normal_file = os.path.join(test_gzip_dir, 'hipster-ipsum.txt')
        gzipped_file = os.path.join(test_gzip_dir, 'hipster-ipsum.txt.gz')

        # Make sure the gzipped file exists
        self.assertTrue(os.path.exists(normal_file), "Normal file does not exist.")
        self.assertTrue(os.path.exists(gzipped_file), "Gzipped file does not exist.")

        # Start the Sipper server with gzip enabled
        sipper = Sipper(test_gzip_dir, gzip=True)
        address = '0.0.0.0'
        port = 8091
        try:
            sipper.start_sipping(address, port)

            def _run_test():
                # Wait for the server to be ready
                self.assertTrue(wait_for_server(address, port), "Server did not start in time.")

                # Simulate an HTTP GET request with gzip accepted using HTTPConnection
                conn = HTTPConnection(address, port)

                url = "/hipster-ipsum.txt"
                # headers = {"Accept-Encoding": "gzip"}
                # Send a GET request with Accept-Encoding: gzip header
                conn.request("GET", url)

                # Get the response
                response = conn.getresponse()

                # Check that the response status code is 200
                self.assertEqual(response.status, 200)

                # If gzip is enabled, check if content is gzipped
                content_encoding = response.getheader('Content-Encoding')
                self.assertEqual(content_encoding, "gzip", "Content is not gzipped.")

                # Read the response content
                response_content = response.read()

                # Verify if the content returned is gzipped (starts with gzip magic bytes)
                self.assertTrue(response_content.startswith(b'\x1f\x8b'), "Response is not gzipped.")
                # Decompress the response body if it's gzipped
                if content_encoding == "gzip":
                    import gzip
                    import io
                    buf = io.BytesIO(response_content)
                    f = gzip.GzipFile(fileobj=buf)
                    decompressed_data = f.read().decode("utf-8")
                    # print("Decompressed Data:", decompressed_data)
                    # Compare the decompressed data against the original file content
                    with open(normal_file, "r", encoding="utf-8") as file:
                        original_data = file.read()

                    # Assert that the decompressed data matches the original file
                    self.assertEqual(decompressed_data, original_data, "Decompressed data does not match the original file content.")
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            # Shutdown the server after the test
            sipper.shutdown(wait_before_shutdown=2)
            sipper.await_sipping_complete()


if __name__ == "__main__":
    unittest.main()
