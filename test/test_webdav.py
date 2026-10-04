import os
import socket
import tempfile
import threading
import time
import unittest
import xml.etree.ElementTree as ET
from http.client import HTTPConnection

from sipper import Sipper


def wait_for_server(address, port, timeout=10):
    """Wait for the server to start."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((address, port), timeout=1):
                return True
        except socket.error:
            time.sleep(0.1)
    return False


class TestWebDAV(unittest.TestCase):
    """Test WebDAV functionality."""

    def setUp(self):
        """Create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.address = '127.0.0.1'
        self.port = 8092

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_webdav_enabled(self):
        """Test that server starts with WebDAV enabled."""
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        try:
            sipper.start_sipping(self.address, self.port)
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_webdav_disabled(self):
        """Test that server starts with WebDAV disabled (default)."""
        sipper = Sipper(self.test_dir, webdav_enabled=False)
        try:
            sipper.start_sipping(self.address, self.port)
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_propfind_single_file_depth_0(self):
        """Test PROPFIND with a single file and depth:0."""
        # Create a single file
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPFIND", "/test.txt", headers={"Depth": "0"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 207, "PROPFIND should return 207 Multi-Status")
            self.assertEqual(response.getheader('Content-Type'), 'text/xml; charset=utf-8')
            
            # Parse XML response
            xml_content = response.read().decode('utf-8')
            root = ET.fromstring(xml_content)
            
            # Check for multistatus root
            self.assertEqual(root.tag, '{DAV:}multistatus')
            
            # Should have exactly one response (the file itself)
            responses = root.findall('{DAV:}response')
            self.assertEqual(len(responses), 1, "Should return exactly one response for depth:0")
            
            # Verify href
            href = responses[0].find('{DAV:}href')
            self.assertIsNotNone(href)
            self.assertIn('test.txt', href.text)
            
            # Verify propstat exists
            propstat = responses[0].find('{DAV:}propstat')
            self.assertIsNotNone(propstat)
            
            # Verify status
            status = propstat.find('{DAV:}status')
            self.assertEqual(status.text, 'HTTP/1.1 200 OK')
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_propfind_nested_depth_0(self):
        """Test PROPFIND with nested structure and depth:0."""
        # Create nested structure
        os.makedirs(os.path.join(self.test_dir, 'subdir'))
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('content1')
        with open(os.path.join(self.test_dir, 'subdir', 'file2.txt'), 'w') as f:
            f.write('content2')

        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPFIND", "/", headers={"Depth": "0"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 207)
            
            xml_content = response.read().decode('utf-8')
            root = ET.fromstring(xml_content)
            
            # Should have exactly one response (the root directory itself)
            responses = root.findall('{DAV:}response')
            self.assertEqual(len(responses), 1, "Should return only root for depth:0")
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_propfind_nested_depth_1(self):
        """Test PROPFIND with nested structure and depth:1."""
        # Create nested structure
        os.makedirs(os.path.join(self.test_dir, 'subdir'))
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('content1')
        with open(os.path.join(self.test_dir, 'subdir', 'file2.txt'), 'w') as f:
            f.write('content2')

        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPFIND", "/", headers={"Depth": "1"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 207)
            
            xml_content = response.read().decode('utf-8')
            root = ET.fromstring(xml_content)
            
            # Should have root + immediate children (file1.txt and subdir)
            responses = root.findall('{DAV:}response')
            self.assertEqual(len(responses), 3, "Should return root and immediate children for depth:1")
            
            # Extract hrefs
            hrefs = [r.find('{DAV:}href').text for r in responses]
            self.assertTrue(any('file1.txt' in h for h in hrefs))
            self.assertTrue(any('subdir' in h for h in hrefs))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_propfind_nested_depth_infinity(self):
        """Test PROPFIND with nested structure and depth:infinity."""
        # Create nested structure
        os.makedirs(os.path.join(self.test_dir, 'subdir', 'nested'))
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('content1')
        with open(os.path.join(self.test_dir, 'subdir', 'file2.txt'), 'w') as f:
            f.write('content2')
        with open(os.path.join(self.test_dir, 'subdir', 'nested', 'file3.txt'), 'w') as f:
            f.write('content3')

        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPFIND", "/", headers={"Depth": "infinity"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 207)
            
            xml_content = response.read().decode('utf-8')
            root = ET.fromstring(xml_content)
            
            # Should have all resources recursively
            responses = root.findall('{DAV:}response')
            self.assertEqual(len(responses), 6, "Should return all resources for depth:infinity")
            
            # Extract hrefs
            hrefs = [r.find('{DAV:}href').text for r in responses]
            self.assertTrue(any('file1.txt' in h for h in hrefs))
            self.assertTrue(any('subdir' in h for h in hrefs))
            self.assertTrue(any('file2.txt' in h for h in hrefs))
            self.assertTrue(any('nested' in h for h in hrefs))
            self.assertTrue(any('file3.txt' in h for h in hrefs))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_mkcol(self):
        """Test MKCOL (create collection/directory)."""
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("MKCOL", "/newdir")
            response = conn.getresponse()
            
            self.assertEqual(response.status, 201, "MKCOL should return 201 Created")
            
            # Verify directory was created
            new_dir = os.path.join(self.test_dir, 'newdir')
            self.assertTrue(os.path.exists(new_dir))
            self.assertTrue(os.path.isdir(new_dir))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_put(self):
        """Test PUT (upload file)."""
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        test_content = b'Test file content'
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PUT", "/uploaded.txt", body=test_content)
            response = conn.getresponse()
            
            self.assertEqual(response.status, 201, "PUT should return 201 Created")
            
            # Verify file was created
            uploaded_file = os.path.join(self.test_dir, 'uploaded.txt')
            self.assertTrue(os.path.exists(uploaded_file))
            
            with open(uploaded_file, 'rb') as f:
                content = f.read()
            self.assertEqual(content, test_content)
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_delete_file(self):
        """Test DELETE (remove file)."""
        test_file = os.path.join(self.test_dir, 'to_delete.txt')
        with open(test_file, 'w') as f:
            f.write('delete me')
        
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("DELETE", "/to_delete.txt")
            response = conn.getresponse()
            
            self.assertEqual(response.status, 204, "DELETE should return 204 No Content")
            
            # Verify file was deleted
            self.assertFalse(os.path.exists(test_file))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_delete_directory(self):
        """Test DELETE (remove empty directory)."""
        test_dir = os.path.join(self.test_dir, 'to_delete_dir')
        os.makedirs(test_dir)
        
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("DELETE", "/to_delete_dir")
            response = conn.getresponse()
            
            self.assertEqual(response.status, 204, "DELETE should return 204 No Content")
            
            # Verify directory was deleted
            self.assertFalse(os.path.exists(test_dir))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_copy(self):
        """Test COPY (copy resource)."""
        test_file = os.path.join(self.test_dir, 'source.txt')
        with open(test_file, 'w') as f:
            f.write('source content')
        
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("COPY", "/source.txt", headers={"Destination": "/dest.txt"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 204, "COPY should return 204 No Content")
            
            # Verify file was copied
            dest_file = os.path.join(self.test_dir, 'dest.txt')
            self.assertTrue(os.path.exists(dest_file))
            
            # Verify source still exists
            self.assertTrue(os.path.exists(test_file))
            
            # Verify content is the same
            with open(test_file, 'r') as f:
                source_content = f.read()
            with open(dest_file, 'r') as f:
                dest_content = f.read()
            self.assertEqual(source_content, dest_content)
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_move(self):
        """Test MOVE (move/rename resource)."""
        test_file = os.path.join(self.test_dir, 'oldname.txt')
        with open(test_file, 'w') as f:
            f.write('move me')
        
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("MOVE", "/oldname.txt", headers={"Destination": "/newname.txt"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 204, "MOVE should return 204 No Content")
            
            # Verify file was moved
            old_file = os.path.join(self.test_dir, 'oldname.txt')
            new_file = os.path.join(self.test_dir, 'newname.txt')
            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(new_file))
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_proppatch(self):
        """Test PROPPATCH (should return 200 OK)."""
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPPATCH", "/")
            response = conn.getresponse()
            
            self.assertEqual(response.status, 200, "PROPPATCH should return 200 OK")
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()

    def test_propfind_nonexistent(self):
        """Test PROPFIND on non-existent resource should return 404."""
        sipper = Sipper(self.test_dir, webdav_enabled=True)
        
        def _run_test():
            self.assertTrue(wait_for_server(self.address, self.port), "Server did not start in time.")
            
            conn = HTTPConnection(self.address, self.port)
            conn.request("PROPFIND", "/nonexistent.txt", headers={"Depth": "0"})
            response = conn.getresponse()
            
            self.assertEqual(response.status, 404, "PROPFIND on non-existent should return 404")
            
            conn.close()
        
        try:
            sipper.start_sipping(self.address, self.port)
            t = threading.Thread(target=_run_test)
            t.start()
            t.join(timeout=10)
        finally:
            sipper.shutdown(wait_before_shutdown=0.5)
            sipper.await_sipping_complete()


if __name__ == "__main__":
    unittest.main()
