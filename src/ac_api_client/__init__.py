# -*- coding: utf-8 -*-
""" ac_api_client - an python client implementation of the restfull webapi of any 
ActiveCollab-instance (http://www.activecollab.com)
"""
import logging, re, collections,urllib2, StringIO, datetime
from lxml import etree

log = logging.getLogger(__name__)

__all__ = ("connect","Credentials",)

PATTERN_DATETIME = "%Y-%m-%d %H:%M:%S"
PATTERN_DATE = "%Y-%m-%d"

def _normalize_xpath_result(data, callback=None):
    try:
        data = "".join(data).strip()
        if not callback is None:
            data = callback(data)
        return data
    except:
        log.error(u"unexcepted error while normalizing a excepted xpath-query-result", exc_info=True)
        return None

def _parse_boolean(data):
    try: return int(data) == 1
    except: return False
        

def _parse_datetime(string, pattern=PATTERN_DATETIME):
    return datetime.datetime.strptime(string, pattern)

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

def forward_property(name, data_member="_data"):
    """ forwarding the value to a requested property name, which is is in a separate data-container
    """
    def getter(self): return _obj_from_chain(data_member, self).get(name)
    def setter(self, value): _obj_from_chain(data_member, self)[name] = value
    return property(getter, setter)

def lazy_property(name, data_member="_data"):
    """ simple property forwarder for handling lazy-loaded property-data
    if the requested property is not available, a callback-command will be 
    initiated to load all the required informations.
    
    most possible that this will be a api-call against  
    """
        
    def getter(self): 
        data = _obj_from_chain(data_member, self).get(name)
        
        if data is None:
            self._refresh()
        
        return _obj_from_chain(data_member, self).get(name)
            
    def setter(self, value):
        source = _obj_from_chain(data_member, self) 
        source
        
        
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
        
        return dict(id=_normalize_xpath_result(doc.xpath("/project/id/text()"), int),
                    name=_normalize_xpath_result(doc.xpath("/project/name/text()")),
                    overview=_normalize_xpath_result(doc.xpath("/project/overview/text()")),
                    status=_normalize_xpath_result(doc.xpath("/project/status/text()")),
                    type=_normalize_xpath_result(doc.xpath("/project/type/text()")),
                    permalink=_normalize_xpath_result(doc.xpath("/project/permalink/text()")),
                    leader=User.create_from_xml(doc.xpath("/project/leader")[0]),
                    company=dict(),
                    group=dict(),
                    logged_user_permissions=dict(),
                    icon_url=_normalize_xpath_result(doc.xpath("/project/icon_url/text()")),
                    )

class TicketsServiceCall(ServiceCallDescriptor):
    """ handles the call for the '/project/*/tickets'-service
    
    build and executes the service call
    handles and transforms the result-list into an list of Ticket-objects
    """

    def result_to_data(self, callback_result):
        """ parse the xml-results into a list of ticket-objects
        """
        doc = callback_result
        tickets = []
        
        for node in doc.xpath("/tickets/ticket"):
            tickets.append(Ticket.create_from_xml(node))
                           
        return tickets
    

class TimeRecordsServiceCall(ServiceCallDescriptor):
    """ handles the call for the '/project/*/time'-service
    
    build and executes the service call
    handles and transforms the result-list into an list of Ticket-objects
    """

    def result_to_data(self, callback_result):
        """ parse the xml-results into a list of ticket-objects
        """
        doc = callback_result
        tickets = []
        
        for node in doc.xpath("/time_records/time_record"):
            tickets.append(TimeRecord.create_from_xml(node))
                           
        return tickets


class Services(object):
    """ a list of all supported activecollab-api calls
    """
    LOAD_PROJECT = ProjectServiceCall(u"/projects/${project_id}")
    LIST_TICKETS = TicketsServiceCall(u"/projects/${project_id}/tickets")
    LIST_TIMERECORDS = TimeRecordsServiceCall(u"/projects/${project_id}/time")

class TimeRecord(object):
    """ wrapping the data about an timerecord and delivers additional functions
    
    this is no dao object, so most property are already available at the time a instance is created
    """
    def __init__(self, data):
        self._data = data

    @classmethod
    def create_from_xml(self, doc):
        return self(data=dict(id=_normalize_xpath_result(doc.xpath("id/text()"), int),
                              
                              ))
        
    id = forward_property("id")
class Ticket(object):
    """ wrapping the data about an ticket and delivers additional functions
    
    this is no dao object, so most property are already available at the time a instance is created
    """
    def __init__(self, data):
        self._data = data

    @classmethod
    def create_from_xml(self, doc):
        return self(data=dict(id=_normalize_xpath_result(doc.xpath("id/text()"), int),
                              type = _normalize_xpath_result(doc.xpath("type/text()")),
                              name = _normalize_xpath_result(doc.xpath("name/text()")),
                              body = _normalize_xpath_result(doc.xpath("body/text()")),
                              state = _normalize_xpath_result(doc.xpath("state/text()"), int),
                              visibility = _normalize_xpath_result(doc.xpath("visibility/text()"), _parse_boolean),
                              created_on = _normalize_xpath_result(doc.xpath("created_on/text()"), _parse_datetime ),
                              created_by_id = _normalize_xpath_result(doc.xpath("created_by_id/text()"), int),
                              updated_on = _normalize_xpath_result(doc.xpath("updated_on/text()"), _parse_datetime),
                              updated_by_id = _normalize_xpath_result(doc.xpath("updated_by_id/text()"), int),
                              version = _normalize_xpath_result(doc.xpath("version/text()"), int),
                              permalink = _normalize_xpath_result(doc.xpath("permalink/text()")),
                              priority = _normalize_xpath_result(doc.xpath("priority/text()"), int),
                              due_on = _normalize_xpath_result(doc.xpath("due_on/text()"), lambda d: _parse_datetime(d, PATTERN_DATE)),
                              completed_on = _normalize_xpath_result(doc.xpath("completed_on/text()"), _parse_datetime),
                              completed_by_id = _normalize_xpath_result(doc.xpath("completed_by_id/text()"), int),
                              tags = _normalize_xpath_result(doc.xpath("tags/text()")),
                              project_id = _normalize_xpath_result(doc.xpath("project_id/text()"), int),
                              parent_id = _normalize_xpath_result(doc.xpath("parent_id/text()"), int),
                              milestone_id = _normalize_xpath_result(doc.xpath("milestone_id/text()"), int),
                              #permissions = _normalize_xpath_result(doc.xpath("permissions/text()"), int),
                              ticket_id = _normalize_xpath_result(doc.xpath("ticket_id/text()"), int),
                              ))
        
    id = forward_property("id")
    type = forward_property("type")
    name = forward_property("name")
    body = forward_property("body")
    state = forward_property("state")
    visibility = forward_property("visibility") 
    created_on = forward_property("created_on")
    created_by_id = forward_property("created_by_id")
    updated_on = forward_property("updated_on")
    updated_by_id = forward_property("updated_by_id")
    version = forward_property("version")
    permalink = forward_property("permalink")
    priority = forward_property("priority")
    due_on = forward_property("due_on")
    completed_on = forward_property("completed_on")
    completed_by_id = forward_property("completed_by_id")
    tags = forward_property("tags")
    project_id = forward_property("project_id")
    parent_id = forward_property("parent_id")
    milestone_id = forward_property("milestone_id")
    permissions = forward_property("permissions")
    ticket_id = forward_property("ticket_id")

class User(object):
    """ wrapping the data about an user and delivers additional functions
    
    this is no dao object, so most property are already available at the time a instance is created
    """
    def __init__(self, data):
        self._data = data
    
    @classmethod
    def create_from_xml(self, doc):
        return self(data=dict(id=_normalize_xpath_result(doc.xpath(".//id/text()"), int),
                              first_name=_normalize_xpath_result(doc.xpath(".//first_name/text()")),
                              last_name=_normalize_xpath_result(doc.xpath(".//last_name/text()")),
                              email=_normalize_xpath_result(doc.xpath(".//email/text()")),
                              last_visit_on=_normalize_xpath_result(doc.xpath(".//last_visit_on/text()"), _parse_datetime),
                              permalink=_normalize_xpath_result(doc.xpath(".//permalink/text()")),
                              role_id=_normalize_xpath_result(doc.xpath(".//role_id/text()"), int),
                              is_administrator=_normalize_xpath_result(doc.xpath(".//is_administrator/text()"), _parse_boolean),
                              is_project_manager=_normalize_xpath_result(doc.xpath(".//is_project_manager/text()"), _parse_boolean),
                              is_people_manager=_normalize_xpath_result(doc.xpath(".//is_people_manager/text()"), _parse_boolean),
                              token=_normalize_xpath_result(doc.xpath(".//token/text()")),
                              company_id=_normalize_xpath_result(doc.xpath(".//company_id/text()"),int),
                              ))
    
    id = forward_property("id")
    first_name = forward_property("first_name")
    last_name = forward_property("last_name")
    email_address = forward_property("email")
    last_visit_on = forward_property("last_visit_on")
    permalink = forward_property("permalink")
    role_id = forward_property("role_id")
    is_administrator = forward_property("is_administrator")
    is_project_manager = forward_property("is_project_manager")
    is_people_manager = forward_property("is_people_manager")
    token = forward_property("token")
    company_id = forward_property("company_id")

class Project(DAO):
    """ Data-Container for the project-data-related informations
    the related propertys are lazy-loaded, with exception of the id-attribute
    """
    def __init__(self, *args, **kvargs):
        super(Project, self).__init__(*args, **kvargs)
        self._time_records = None
        self._tickets = None
        
    def _refresh(self):
        self._data = Services.LOAD_PROJECT.call(self._proxy,project_id=self.id)
        
    name = lazy_property("name")
    overview = lazy_property("overview")
    status = lazy_property("status")
    type = lazy_property("type")
    permalink = lazy_property("permalink")
    leader = lazy_property("leader")
    company = lazy_property("company")
    group = lazy_property("group"),
    logged_user_permissions = lazy_property("logged_user_permissions")
    icon_url = lazy_property("icon_url")
    
    
    @property
    def time_records(self):
        if self._time_records is None:
            manager = ProjectManager(self._proxy)
            self._time_records = manager.list_time_records_for_project(self.id)
        return self._time_records
        
    @property
    def tickets(self):
        if self._tickets is None:
            manager = ProjectManager(self._proxy)
            self.timerecords = manager.list_tickets_for_project(self.id)
        return self._tickets
        

    

class ProjectManager(object):
    """ distributes methods to load one or more projects
    """
    def __init__(self, proxy):
        self._proxy = proxy

    def list_tickets_for_project(self, project_id):
        return Services.LIST_TICKETS.call(self._proxy, project_id=project_id)
    
    def list_time_records_for_project(self, project_id):
        return Services.LIST_TIMERECORDS.call(self._proxy, project_id=project_id)
    
    def load(self, id):
        """ returns a lazy-loading project-object
        """
        return Project(self._proxy, id=id)
        
    