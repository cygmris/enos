__author__ = 'lomax'
"""
    This package provides generic type and basic implementation of OpenFlow support. Note tha it currently
    does not provide any level of security, nor it is thread safe. This will have to be addressed in the future.
"""
from commom.utils import generateId
from common.api import Properties


class FlowMod:
    """
    This class uniquely represent a flow mod.
    """
    def __init__(self,scope,matches,actions):
        self.scope =  scope
        self.matches = matches
        self.actions = actions
        self.id = generateId()

class Scope(Properties):
    """
    This class is a Properties wrapper. The key/value pairs in the property is used to define the scope of control
    an application wishes to have on a given network element.
    """
    def __init__(self,name,switch,owner,props={}):
        """
        :param name: str human readable name of the scope
        :param switch: OpenFlowSwitch target switch
        :param owner: ScopeController controller that owns this scope
        :param props: dict optional properties of the scope, such as ports, vlan, etc. See Layer2Scope for example.
        """
        Properties.__init__(self,name,props)
        self.switch = switch
        self.owner = owner

    def overlaps(self, scope):
        """
        Check if this scopes overlaps with the provided scope. It is expected that Scope implements will overwrite
         this method.
        :param scope: Scope
        :returns True if scopes overlap, False otherwise
        """
        return True



class ScopeEvent(Properties):
    """
    This class define an event related to a scope sent by the controller to the application. Scope implementation
    are responsible for implementing ScopeEvent as well. A ScopeEvent is a Properties, i.e. a dict of objects.
    For instance, an OpenFlow event could countain a key "packet-in" matching an object containing the relevant
    data. Implementing scopes freely define their own key/value pairs. All keys must be strings.

    This base class defines basic keys as well as their meaning. Value definition is let to the implementation.
    However the semantic of the key must be followed. This allow the consumer of the
    event to understand what the event means without understand the actual details, or the opposite.

        "closed": the scope has closed. If there is no "error" key/value in the event, the scope is gracefully closed.
        "error": the event is the result of an error that affected the scope.
        "changed": something has changed in the scope.
    """
    def __init__(self,name,scope,props={}):
        """
        :param name: str  human readable name of the event
        :param scope: Scope scope that is generating the event
        :param props: properties of the event
        """
        Properties.__init__(self,name,props={})
        self.id = generateId()


class ScopeController():
    """
    This class must be extended by any application that controls a scope.
    """
    def __init__(self):
        self.controller = None # The controller will set it ip

    def eventListener(self,event):
        """
        The implementation of this class is expected to overwrite this method if it desires
        to receive events from the controller such as PACKET_IN
        :param event: ScopeEvent
        """


class Layer2Scope(Scope):
    """
    This class is the base class of any Scope that defines a layer 2 switch
    """
    def __init__(self,name,switch,owner,props={},endpoints=[]):
        """
        Creates a Layer2Scope. The optional endpoint parameter is a list that contains tuples. Tuples are expected
        to be (port,vlans), where port is a string and vlans is a list of integers. The following are valid examples:
            ("eth10",[12]) port eth10, VLAN 12
            ("eth10,[])  the whole eth10 port (any VLAN)
            ("eth10,[1,2,3]) VLAN 1, 2 and 3 on port eth10
            ("eth10, [range(1000,2000)] all VLAN from 1000 to 1999 on port eth10
        If no endpoint is provided, then the scope represents all VLAN on all ports
        """
        Scope.__init__(self,name,switch,owner,props)
        self.props['endpoints'] = endpoints



class OpenFlowSwitch:
    """
    This class represents an OpenFlowSwitch. It contains the list of flowmods that is set on the switch.
    """
    def __init__(self, controller):
        """
        Creates an OpenFlowSwitch instance.
        :param controller (Controller) of this switch
        :return:
        """
        self.controller = controller
        self.flowMods = {}
        self.scopes = {}




class Controller:
    """
    This class defined the generic API of the client of an OpenFlow controller.
    API for packet in and out not yet defined.
    """
    def requestControl(self,scope):
        """
        Request the control over the specified scope.
        :param scope:
        :return: True up success, False otherwise
        """
        return False

    def addFlowMod(self, flowMod):
        print "not implemented"

    def delFlowMod(self, flowMod):
        print "not implemented"


class SimpleController(Controller):
    """
    This class implements a simple controller. It implements some basic controller function but does not
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implements a singleton
        """
        if not cls._instance:
            cls._instance = super(SimpleController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.scopes = {}
        self.forbiddenScopes = {}
        self.switches = {}
        self.id = generateId()

    def addSwitch(self,switch):
        """
        Adds a switch to the list of switches this controller can manage
        :param switch: OpenFlowSwitch
        :return:
        """
        self.switches[switch.dpid] = switch

    def removeSwitch(self,switch):
        self.switches.pop(switch)
        # Remove all flow mods on that switch
        self.scopes = {}
        for flowMod in switch.flowMods():
            self.delFlowMod(flowMod)

    def addScope(self,scope):
        """
        Adds the scopes to the authorized set of scopes. In order to be accepted, a scope must not overlap
        with any of the forbiden scopes, and not overlap with any of existing, authorized, scopes, unless it
        has the same owner than the provided owner.
        :param scope:
        :return:
        """
        for (x,s) in self.forbiddenScopes.elems():
            if s.overlaps(scope):
                return False
        for (x,s) in self.scopes:
            if s.overlaps(scope) and id(s.owner) != id(scope.owner):
                return False
        if scope.id in self.scopes.keys():
            return False
        self.scopes[scope.id] = scope
        return  True

    def removeScope(self,scope):
        self.scopes.pop(scope)


    def addForbidenScope(self,scope):
        """
        Adds a scope that is forbidden to authorize any request
        :param scope:
        :return:
        """
        print "not implemented yet"

    def removeForbidenScope(self,scope):
        """
        Adds a scope that is forbidden scope
        :param scope:
        :return:
        """
        print "not implemented yet"

    def addFlowMod(self, flowMod):
        print "[" + str(scope.switch) + "] adding flowMod " + str(flowMod)

    def delFlowMod(self, flowMod):
        print "[" + str(scope.switch) + "] removing flowMod " + str(flowMod)





