# -*- coding: utf-8 -*-
import unittest, mox
import ac_api_client
from lxml import etree
import StringIO

class TestProjectServiceCall(unittest.TestCase):
    def setUp(self):
        self._mocker = mox.Mox()
        self._credentials = ac_api_client.Credentials(None, None)

    def test_call(self):
        service = ac_api_client.Services.LOAD_PROJECT

        proxy = self._mocker.CreateMock(ac_api_client.Proxy)
        proxy.call(u"/projects/1").AndReturn("""<?xml version="1.0" encoding="UTF-8"?><project><id>1</id><name>foo</name></project>""")
        
        self._mocker.ReplayAll()

        data = service.call(proxy,project_id=1)
        
        self.assertFalse(data is None)
        self.assertTrue(type(data) is dict)
        self.assertEqual(data["id"],1)
        self.assertEqual(data["name"],u"foo")