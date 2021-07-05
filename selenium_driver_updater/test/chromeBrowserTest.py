#Standart library imports
import unittest
import os.path
import time
import logging
import platform

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

# Local imports
from _setting import setting
from browsers._chromeBrowser import ChromeBrowser
from util.requests_getter import RequestsGetter

logging.basicConfig(level=logging.INFO)

# pylint: disable=missing-function-docstring
class testChromeBrowser(unittest.TestCase):
    """Class for unit-testing ChromeBrowser class

    Attributes:
        path (str)              : Specific path where test drivers located
        chrome_driver           : Initialize class ChromeDriver
        startTime (float)       : Time of starting unit-tests
        setting (dict[str])     : Dict of all additional parametres
        specific_version (str)  : Specific version of chromedriver to test
    """

    @classmethod
    def setUpClass(cls):
        cls.setting = setting

        driver_name : str = "chromedriver_test.exe" if platform.system() == 'Windows' else\
                                        "chromedriver_test"

        path : str = str(setting["Program"]["driversPath"]) + driver_name

        cls.chromebrowser = ChromeBrowser(path=path, check_browser_is_up_to_date = True)
        cls.requests_getter = RequestsGetter

    @classmethod
    def tearDownClass(cls):
        del cls.chromebrowser

    def setUp(self):

        self.start_time : float = time.time()

    def tearDown(self):
        end_time = time.time() - self.start_time
        print("%.3f" % end_time)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = self.setting["ChromeBrowser"]["LinkAllLatestRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_current_version_chrome_selenium(self):
        result, message, current_version = self.chromebrowser._ChromeBrowser__get_current_version_chrome_browser_selenium()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreater(len(current_version), 0, len(current_version))

    #@unittest.skip('Temporary not needed')
    def test03_check_get_latest_version_chrome_browser(self):
        result, message, latest_version = self.chromebrowser._ChromeBrowser__get_latest_version_chrome_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test04_check_get_latest_chrome_browser_for_current_os(self):
        result, message = self.chromebrowser._ChromeBrowser__get_latest_chrome_browser_for_current_os()
        self.assertTrue(result, message)

    #@unittest.skip('Temporary could not test it on Github Workflow')
    def test05_check_compare_current_version_and_latest_version_chrome_browser(self):
        result, message, is_browser_is_up_to_date, current_version, latest_version = self.chromebrowser._ChromeBrowser__compare_current_version_and_latest_version_chrome_browser()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_browser_is_up_to_date, is_browser_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertIn(is_browser_is_up_to_date, [True, False], is_browser_is_up_to_date)

        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))

    #@unittest.skip('Temporary not needed')
    def test06_check_chromedriver_is_up_to_date(self):
        result, message = self.chromebrowser.main()
        self.assertTrue(result, message)


if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)
