# -*- coding: utf-8 -*-
import unittest
import ac_api_client
import mox

import ConfigParser

class DefaultTestCase(unittest.TestCase):
    def setUp(self):
        cp = ConfigParser.RawConfigParser()
        cp.read("tests/config.ini")
        
        self.config = dict()
        
        for item in cp.items("default"):
            self.config[item[0]] = item[1]  
        
        


class TestProjectManager(DefaultTestCase):
    def test_load(self):
        proxy = ac_api_client.Proxy(ac_api_client.Credentials(self.config["base_url"],
                                                              self.config["token"]
                                                              ))
        manager = ac_api_client.ProjectManager(proxy)
        
        project = manager.load(106)
        
        self.assertEqual(project.id, 106)
        self.assertFalse(project.name is None)