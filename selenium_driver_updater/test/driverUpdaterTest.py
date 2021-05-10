import unittest

import sys
import os.path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from driverUpdater import DriverUpdater
from _setting import setting
import time
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

import requests

import json

class testDriverUpdater(unittest.TestCase): 
    """Class for unit-testing DriverUpdater class

    Attributes:
        startTime (float)           : Time of starting unit-tests
    """

    def setUp(self):

        user_agent : str = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/35.0.1916.47 Safari/537.36'

        self.headers = {'User-Agent': user_agent}

        self.setting = setting

        self.startTime : float = time.time()

        self.driver_updater = DriverUpdater

    def tearDown(self):
        t = time.time() - self.startTime
        print("%.3f" % t)

    #@unittest.skip('Temporary not needed')
    def test01_check_get_result_by_request(self):
        url = self.setting["PyPi"]["urlProjectJson"]
        request = requests.get(url=url, headers=self.headers)
        status_code = request.status_code
        request_text = request.text

        self.assertEqual(status_code, 200, status_code)
        self.assertGreater(len(request_text), 0, request_text)
    
    #@unittest.skip('Temporary not needed')
    def test02_check_library_is_up_to_date(self):
        result, message = self.driver_updater._DriverUpdater__check_library_is_up_to_date()
        self.assertTrue(result, message)
    
    
if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=True, exit=False)