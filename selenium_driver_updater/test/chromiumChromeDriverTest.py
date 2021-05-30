import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from _setting import setting
from _chromiumChromeDriver import ChromiumChromeDriver
from util.requests_getter import RequestsGetter

import time
import logging
logging.basicConfig(level=logging.INFO)

class testChromiumChromeDriver(unittest.TestCase): 
    """Class for unit-testing ChromiumChromeDriver class

    Attributes:
        chromium_chromedriver   : Initialize class ChromiumChromeDriver
        startTime (float)       : Time of starting unit-tests
    """

    @classmethod
    def setUpClass(cls):

        cls.setting = setting

        cls.chromium_chromedriver = ChromiumChromeDriver(check_driver_is_up_to_date = True, check_browser_is_up_to_date = False)

        cls.requests_getter = RequestsGetter
        
    @classmethod
    def tearDownClass(cls):
        del cls.chromium_chromedriver

    def setUp(self):

        self.startTime : float = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = self.setting["ChromeDriver"]["LinkLastRelease"]
        result, message, status_code, json_data = self.requests_getter.get_result_by_request(url=url)
        self.assertTrue(result, message)
        self.assertEqual(status_code, 200, status_code)
        self.assertGreaterEqual(len(json_data), 0, len(json_data))

    #@unittest.skip('Temporary not needed')
    def test02_check_get_current_version_chromium_chromedriver(self):
        result, message, current_version = self.chromium_chromedriver._ChromiumChromeDriver__get_current_version_chromium_chromedriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(current_version, current_version)
        self.assertGreaterEqual(len(current_version), 0, len(current_version))
    
    #@unittest.skip('Temporary not needed')
    def test03_check_get_latest_version_chromium_chromedriver(self):
        result, message, latest_version = self.chromium_chromedriver._ChromiumChromeDriver__get_latest_version_chromium_chromedriver()
        self.assertTrue(result, message)
        self.assertIsNotNone(latest_version, latest_version)
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
    #@unittest.skip('Temporary not needed')
    def test04_check_get_latest_chromium_chromedriver_for_current_os(self):
        result, message, driver_path = self.chromium_chromedriver._ChromiumChromeDriver__get_latest_chromium_chromedriver_for_current_os()
        self.assertTrue(result, message)
        self.assertIsNotNone(driver_path, driver_path)
        self.assertGreaterEqual(len(driver_path), 0, len(driver_path))
    
    #@unittest.skip('Temporary not needed')
    def test05_check_compare_current_version_and_latest_version(self):
        result, message, is_driver_is_up_to_date, current_version, latest_version = self.chromium_chromedriver._ChromiumChromeDriver__compare_current_version_and_latest_version()
        self.assertTrue(result, message)
        self.assertIsNotNone(is_driver_is_up_to_date, is_driver_is_up_to_date)
        self.assertIsNotNone(current_version, current_version)
        self.assertIsNotNone(latest_version, latest_version)

        self.assertTrue(is_driver_is_up_to_date, is_driver_is_up_to_date)
        
        self.assertGreater(len(current_version), 0, len(current_version))
        self.assertGreater(len(latest_version), 0, len(latest_version))
    
     #@unittest.skip('Temporary not needed')
    def test06_check_chromedriver_is_up_to_date(self):
        result, message, filename = self.chromium_chromedriver.main()
        self.assertTrue(result, message)
        self.assertGreaterEqual(len(filename), 0, len(filename))

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)