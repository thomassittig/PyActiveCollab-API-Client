# -*- coding: utf-8 -*-
""" ac_api_client - an python client implementation of the restfull webapi of any 
ActiveCollab-instance (http://www.activecollab.com)
"""
import logging, re, collections,urllib2, StringIO
from lxml import etree

log = logging.getLogger(__name__)

__all__ = ("connect","Credentials",)

def lazy_property(name, data_member="_data"):
    """ simple property forwarder for handling lazy-loaded property-data
    if the requested property is not available, a callback-command will be 
    initiated to load all the required informations.
    
    most possible that this will be a api-call against  
    """
    def _validate_container_type(data):
        """ the container as to be a dictionary
        """
        return type(data) is dict
        
    def _obj_from_chain(chain_key, current_dom):
        for attr_name in chain_key.split("."):
            current_dom = getattr(current_dom, attr_name)
        
        if _validate_container_type(current_dom):
            return current_dom
        
        raise TypeError(u"containers has to be from type dict")
        
    def getter(self): 
        data = _obj_from_chain(data_member, self).get(name)
        
        if data is None:
            self._refresh()
        
        return _obj_from_chain(data_member, self).get(name)
            
    def setter(self, value):
        source = _obj_from_chain(data_member, self) 
        source[name] = value
        
        
    return property(getter, setter)

class DAO(object):
    def __init__(self, proxy, id=None, data=dict()):
        self._data = data
        self._proxy = proxy
        self.id = id

    def _refresh(self):
        raise Exception(u"please implement me")        
    
Credentials = collections.namedtuple("Credentials", "base_url token")
    
class Proxy(object):
    """ The ServiceProxy handles the direct URL-call to the remote server and also its response
    """
    def __init__(self, credentials):
        self._credentials = credentials
        
    def _build_url(self, credentials, cmd_path):
        return "%s?path_info=%s&token=%s" % (credentials.base_url, cmd_path, credentials.token)
    
    def call(self, url, **args):
        response = None
        try:
            url = self._build_url(self._credentials, url)
            log.debug(u"open url for %s with data" % url)
            
            request_args = dict(url=url)
            
            if len(args)>0:
                request_args["data"] = args
                
            request = urllib2.Request(**request_args)
            
            f = urllib2.urlopen(request)
            response = f.read()
        except urllib2.HTTPError:
            log.error(u"the requested url could not be opened", exc_info = False)
        
        return response
    
class ServiceCallDescriptor(object):
    """ abstract descriptor to descripe a common ServiceCall-object
    """
    def __init__(self,raw_command):
        self._raw_command = raw_command

    def _translate_cmd(self, cmd, **args):
        for k,v in args.iteritems():
             
            cmd = cmd.replace(u"${%s}" % k,str(v))
        return cmd
    
    def _handle_xml_result(self, xml_data):
        return etree.parse(StringIO.StringIO(xml_data))

    def result_to_data(self, callback_result):
        raise Exception(u"no implemention here!")
    
    def call(self, proxy, **args):
        """ default service-call
        
        all the arguments in args will be passed to the call as post-arguments
        """
        data = proxy.call(self._translate_cmd(self._raw_command, **args))
        doc = self._handle_xml_result(data)
        return self.result_to_data(doc)

class ProjectServiceCall(ServiceCallDescriptor):
    """ handles the call for the '/project/'-service
    
    build and executes the service call
    handles and transforms the result into an dictionary
    """

    def result_to_data(self, callback_result):
        doc = callback_result
        return dict(id=int("".join(doc.xpath("/project/id/text()"))),
                    name="".join(doc.xpath("/project/name/text()")),
                    overview="".join(doc.xpath("/project/overview/text()")),
                    status="".join(doc.xpath("/project/status/text()")),
                    type="".join(doc.xpath("/project/type/text()")),
                    permalink="".join(doc.xpath("/project/permalink/text()")),
                    leader=dict(),
                    company=dict(),
                    group=dict(),
                    logged_user_permissions=dict(),
                    icon_url="".join(doc.xpath("/project/icon_url/text()")),
                    )

class Services(object):
    """ a list of all supported activecollab-api calls
    """
    LOAD_PROJECT = ProjectServiceCall(u"/projects/${project_id}")


class Project(DAO):
    """ Data-Container for the project-data-related informations
    the related propertys are lazy-loaded, with exception of the id-attribute
    """
    def __init__(self, *args, **kvargs):
        super(Project, self).__init__(*args, **kvargs)
        
    def _refresh(self):
        self._data = Services.LOAD_PROJECT.call(self._proxy,project_id=self.id)
        
    name = lazy_property("name")

class ProjectManager(object):
    """ distributes methods to load one or more objects
    """
    def __init__(self, proxy):
        self._proxy = proxy
    
    def load(self, id):
        """ returns a lazy-loading project-object
        """
        return Project(self._proxy, id=id)
        
    