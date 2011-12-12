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
    
    def test_init(self):
        proxy = self._mocker.CreateMock(ac_api_client.Proxy)
        proxy.call(u"/projects/1").AndReturn(None)
        
        self._mocker.ReplayAll()
        
        manager = ac_api_client.ProjectManager(proxy)
        project = manager.load(1)
        
        self.assertTrue(project is None)
    
    def test_load(self):
        pass