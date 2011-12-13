# -*- coding: utf-8 -*-
import unittest
import ac_api_client
import mox

class TestProjectManager(unittest.TestCase):
    def setUp(self):
        self._mocker = mox.Mox()
        self._credentials = ac_api_client.Credentials(None, None)
    
    def tearDown(self):
        pass
    
    def test_load(self):
        pass