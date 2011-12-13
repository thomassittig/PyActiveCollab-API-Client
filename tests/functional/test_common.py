# -*- coding: utf-8 -*-
import unittest, datetime
import ac_api_client
from lxml import etree
from StringIO import StringIO

class TestProxy(unittest.TestCase):
    def test_call(self):
        proxy = ac_api_client.Proxy(ac_api_client.Credentials("http://www.google.com", ""))
        result = proxy.call(u"/")
        self.assertFalse(result is None)
        
    
class TestUser(unittest.TestCase):
    def test_create_from_node(self):
        user = ac_api_client.User.create_from_xml(etree.parse(StringIO("""<leader><id>1</id><first_name><![CDATA[ Foo ]]></first_name><last_name><![CDATA[ Bar ]]></last_name><email><![CDATA[ foo@bar.com ]]></email><last_visit_on>2011-01-01 08:00:00</last_visit_on><permalink><![CDATA[https://www.foobar.com/]]></permalink><role_id>2</role_id><is_administrator>1</is_administrator><is_project_manager>0</is_project_manager><is_people_manager>1</is_people_manager><token><![CDATA[ foobartoken ]]></token><company_id>3</company_id></leader>""")))
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.first_name, "Foo")
        self.assertEqual(user.last_name, "Bar")
        self.assertEqual(user.email_address, "foo@bar.com")
        self.assertEqual(user.last_visit_on, datetime.datetime(2011,1,1,8,0,0))
        self.assertEqual(user.permalink, u"https://www.foobar.com/")
        self.assertEqual(user.role_id, 2)
        self.assertEqual(user.is_administrator, True)
        self.assertEqual(user.is_project_manager, False)
        self.assertEqual(user.is_people_manager, True)
        self.assertEqual(user.token, u"foobartoken")
        self.assertEqual(user.company_id, 3)
        
        
        
