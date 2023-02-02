import unittest
from sipper import Sipper


class TestApplication(unittest.TestCase):
    """ Checking if command-line args work """

    def test_directory(self):
        sipper = Sipper("/")
        self.assertEqual(sipper.directory, '/')

    def test_show_directory_listings(self):
        sipper = Sipper('/')
        self.assertEqual(sipper.show_directory_listings, True)

    def test_shutdown(self):
        sipper = Sipper('/')
        sipper.start_sipping('0.0.0.0', 8089)
        sipper.shutdown(wait_before_shutdown=2)


if __name__ == '__main__':
    unittest.main()
