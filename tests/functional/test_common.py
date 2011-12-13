# -*- coding: utf-8 -*-
import unittest
import ac_api_client

class TestProxy(unittest.TestCase):
    def test_call(self):
        proxy = ac_api_client.Proxy(ac_api_client.Credentials("http://www.google.com", ""))
        result = proxy.call(u"/")
        self.assertFalse(result is None)