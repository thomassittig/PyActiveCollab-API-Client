# -*- coding: utf-8 -*-
import unittest
import ac_api_client
import mox

import ConfigParser

class DefaultTestCase(unittest.TestCase):
    def setUp(self):
        cp = ConfigParser.RawConfigParser()
        cp.read("./../../tests/config.ini")
        
        self.config = dict()
        
        for item in cp.items("default"):
            self.config[item[0]] = item[1]  
        
        


class TestProjectManager(DefaultTestCase):
    def setUp(self):
        super(TestProjectManager, self).setUp()
        self.default_proxy = ac_api_client.Proxy(ac_api_client.Credentials(self.config["base_url"],
                                                              self.config["token"]
                                                              ))
    
    def test_load(self):
        manager = ac_api_client.ProjectManager(self.default_proxy)
        
        project = manager.load(106)
        
        self.assertEqual(project.id, 106)
        self.assertFalse(project.name is None)
        self.assertFalse(project.leader is None)
        self.assertFalse(project.leader.first_name is None)


    def test_list_tickets_for_project(self):
        manager = ac_api_client.ProjectManager(self.default_proxy)
        
        tickets = manager.list_tickets_for_project(106)
        
        self.assertTrue(len(tickets)>0)
        
        ticket = tickets.pop()
        
        self.assertFalse(tickets.pop().id is None)
        self.assertFalse(tickets.pop().type is None)
        self.assertFalse(tickets.pop().name is None)
        
    def test_list_time_records_for_project(self):
        manager = ac_api_client.ProjectManager(self.default_proxy)
        
        timerecords = manager.list_time_records_for_project(106)
        
        self.assertTrue(len(timerecords)>0)
        
