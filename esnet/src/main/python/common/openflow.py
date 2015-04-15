__author__ = 'lomax'
"""
    This package provides generic type and basic implementation of OpenFlow support. Note tha it currently
    does not provide any level of security, nor it is thread safe. This will have to be addressed in the future.
"""
from common.utils import generateId
from common.api import Properties, Node


class Match(Properties):
    """
    This is the class defining an OpenFlow match. It is a wrapper of Properties.
    The base class defines the following key / values:

    Layer2:
        "in_port": Port ingress port on the swith
        "dl_src" : array('B') source MAC
        "dl_dst" : array('B') destination MAC
        "vlan"   : int VLAN

    Other layers are TBD

    """
    def __init__(self,name=None,props={}):
        Properties.__init__(self,name,props)

class Action(Properties):
    """
    This class is the class defining an OpenFlow action. It is a wrapper of Properties.
    The base class defines the following key / values:

    Layer 2:
        "dl_src": array('B') rewrite the source MAC with the provided MAC
        "dl_dst": array('B') rewrite the destination MAC with the provided MAC
        "vlan": int rewrite the VLAN with the provided vlan
        "out_port": Port list of egress ports

    Other layers are TBD
    """
    def __init__(self,name=None,props={}):
        Properties.__init__(self,name,props)



class FlowMod(Properties):
    """
    This class uniquely represent a flow mod.
    """
    def __init__(self,scope,switch,match=None,name="",actions=[]):
        """
        :param scope: Scope owner
        :param switch: common.api.Node
        :param match: Match
        :param actions: Action
        """
        Properties.__init__(self,name)
        self.scope = scope
        self.scopeowner = scope.owner
        self.switch = switch
        self.actions = actions
        self.match = match
        self.id = generateId()


class Scope(Properties):
    """
    This class is a Properties wrapper. The key/value pairs in the property is used to define the scope of control
    an application wishes to have on a given network element.
    """
    def __init__(self,name,switch,owner,props={}):
        """
        :param name: str human readable name of the scope
        :param switch: common.api.Node
        :param owner: ScopeController controller that owns this scope
        :param props: dict optional properties of the scope, such as ports, vlan, etc. See Layer2Scope for example.
        """
        Properties.__init__(self,name,props)
        self.owner = owner
        self.id = generateId()
        self.switch = switch

    def overlaps(self, scope):
        """
        Check if this scopes overlaps with the provided scope. It is expected that Scope implements will overwrite
         this method.
        :param scope: Scope
        :returns True if scopes overlap, False otherwise
        """
        return True

    def isValidFlowMod(self, flowMod):
        """
        Verifies if a flowMod is valid within the scope
        :param flowMod: FlowMod
        """
        return False



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

class PacketInEvent(ScopeEvent):
    """
    This class defines a PACKET_IN event. It adds the following key / value's to the ScopeEvent

        "in_port": str ingress port
        "payload": str payload of the packet
    Layer 2
        "dl_src": str source MAC
        "dl_dst": str destination MAC
        "vlan" ": int VLAN

     Other layers are TBD
    """

    def __init__(self,inPort,srcMac,dstMac,vlan=None,payload=None,name="",):
        Properties.__init__(self,name)
        self.props['in_port'] = inPort
        self.props['dl_src'] = srcMac
        self.props['dl_dst'] = dstMac
        if vlan:
            self.props['vlan'] = vlan
        if payload:
            self.props['payload'] = payload


class PacketOut(Properties):
    """
    This class implements a packet out.
    """
    def __init__(self,scope,port,vlan,payload,name=""):
        """
        :param scope: Scope
        :param port: Port
        :param vlan: int
        :param payload: array('B')
        """
        Properties.__init__(self,name)
        self.scope = scope
        self.port = port
        self.vlan = vlan
        self.payload = payload

    def __str__(self):
        return self.port.name + "/" + str(self.vlan) + " " + str(self.payload)

    def __repr__(self):
        return self.__str__()

class ScopeOwner():
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


class L2SwitchScope(Scope):
    """
    This class is the base class of any Scope that defines a layer 2 switch
    """
    def __init__(self,name,switch,owner,props={},endpoints=[]):
        """
        Creates a Layer2Scope. The optional endpoint parameter is a list that contains tuples. Tuples are expected
        to be (port,vlans), where port is a string and vlans is a list of integers. The following are valid examples:
            ("eth10",[12]) port eth10, VLAN 12
            ("eth10",[])  the whole eth10 port (any VLAN)
            ("eth10",[1,2,10]) VLAN 1, 2 and 10 on port eth10
        If no endpoint is provided, then the scope represents all VLAN on all ports
        """
        Scope.__init__(self,name,switch,owner,props)
        self.props['endpoints'] = endpoints

    def overlaps(self, scope):
        endpoints1 = self.props['endpoints']
        if not 'endpoints' in scope.props:
            # not a L2SwitchScope
            return False
        endpoints2 = scope.props['endpoints']
        # If not the same switch, they don't overlap
        if self.switch != scope.switch:
            return False
        # If either set of endpoints is empty, they trivially overlap
        if len(endpoints1) == 0 or len(endpoints2) == 0:
            return True
        for endpoint1 in endpoints1:
            port1 = endpoint1[0]
            vlans1 = endpoint1[1]
            for endpoint2 in endpoints2:
                port2 = endpoint2[0]
                vlans2 = endpoint2[1]
                if port1 != port2:
                    # not same port, therefore no overlap
                    continue
                # check vlans
                for vlan1 in vlans1:
                    for vlan2 in vlans2:
                        if vlan1 == vlan2:
                            # overlap
                            return True
        return False

    def isValidPacketOut(self,packet):

        endpoints = self.props['endpoints']
        for port,vlans in endpoints:
            if port != packet.port.name:
                continue
            if packet.vlan in vlans:
                return True
        return False

    def isValidFlowMod(self, flowMod):
        """
        Check to see if a flow is contained within this scope
        """
        match = flowMod.match
        actions = flowMod.actions
        switch = flowMod.switch

        endpoints = self.props['endpoints']
        # See if it's for the same switch.  If not, it can't be valid.
        if switch != self.switch:
            return False

        # If no endpoints, then the scope covers all VLANs and ports and the flow must be valid.
        if len(endpoints) == 0:
            return True

        if not 'in_port' in match.props:
            # This controller rejects matches that do not include an in_port
            return False

        in_port = match.props['in_port'].name
        in_vlan = match.props['vlan']
        valid = False
        # checks match
        for endpoint in endpoints:
            port = endpoint[0]
            if port != in_port:
                continue
            vlans = endpoint[1]
            for vlan in vlans:
                if vlan == in_vlan:
                    # authorized vlan
                    valid = True
                    break
        if not valid:
            return False
        # check actions
        for action in actions:
            out_port = action.props['out_port'].name
            out_vlan = action.props['vlan']
            valid = False
            for endpoint in endpoints:
                port = endpoint[0]
                if port != out_port:
                    continue
                vlans = endpoint[1]
                if not out_vlan in vlans:
                    return False
                else:
                    valid = True
                    break
            if not valid:
                return False
        return True


class OpenFlowSwitch(Node):
    """
    This class represents an OpenFlowSwitch. It contains the list of flowmods that is set on the switch.
    """
    def __init__(self, name, dpid, controller = None, builder = None, props = {}):
        """
        Creates an OpenFlowSwitch instance.
        :param controller (Controller) of this switch
        :return:
        """
        Node.__init__(self, name, builder, props)
        self.dpid = dpid
        self.controller = controller
        self.flowMods = {}
        self.scopes = {}


class Controller(object):
    """
    This class defined the generic API of the client of an OpenFlow controller.
    API for packet in and out not yet defined.
    """
    def __init__(self):
        return

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

    def send(selfs,packet):
        """
        :param packet: PacketOut
        """


class SimpleController(Controller):
    """
    This class implements a simple controller. It implements some basic controller function but does not
    implement the actual interaction with the switch or controller.
    """

    def __init__(self):
        super(SimpleController,self).__init__()
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
        for (x,s) in self.forbiddenScopes.iteritems():
            if s.overlaps(scope):
                return False
        for (x,s) in self.scopes.iteritems():
            if s.overlaps(scope) and id(s.owner) != id(scope.owner):
                return False
        if scope.id in self.scopes.keys():
            return False
        self.scopes[scope.id] = scope
        return  True

    def removeScope(self,scope):
        self.scopes.pop(scope)


    def addForbiddenScope(self,scope):
        """
        Adds a scope that is forbidden to authorize any request
        :param scope:
        :return:
        """
        print "not implemented yet"

    def removeForbiddenScope(self,scope):
        """
        Adds a scope that is forbidden scope
        :param scope:
        :return:
        """
        print "not implemented yet"

    def isFlowModValid(self, flowMod):
        scopeId = flowMod.scope.id
        if not scopeId in self.scopes:
            return False
        scope = self.scopes[scopeId]
        return scope.isValidFlowMod(flowMod)

    def isPacketOutValid(self,packet):
        scopeId = packet.scope.id
        if not scopeId in self.scopes:
            return False
        scope = self.scopes[scopeId]
        return scope.isValidPacketOut(packet)

    def addFlowMod(self, flowMod):
        """
        Implementation of SimpleController must implement this method
        :param flowMod:
        :return:
        """
        return False

    def delFlowMod(self, flowMod):
        """
        Implementation of SimpleController must implement this method
        :param flowMod:
        :return:
        """
        return False

    def send(self,packet):
        """
        Implementation of SimpleController must implement this method
        :param self:
        :param packet:
        :return:
        """
        return False

    @staticmethod
    def makeL2FlowMod(scope, switch, inPort, inVlan, outPort, outVlan):
        """
        Convenience method to make a flow entry for Layer 2 / VLAN translation.
        Note that the returned flow entry only handles one direction of
        translation / forwarding; for use in a bidirectional circuit (i.e.
        OSCARS semantics), two of these are required.
        :param switch: the switch to which this flow entry applies
        :param inPort: input port
        :param inVlan: input VLAN tag
        :param outPort: output port
        :param outVlan: output VLAN tag
        :return: FlowMod
        """
        match = Match()
        match.props['in_port'] = inPort
        match.props['vlan'] = inVlan

        actions = Action()
        actions.props['vlan'] = outVlan
        actions.props['out_port'] = { outPort }

        flow = FlowMod(scope=scope, switch=switch, match=match, actions=actions)
        return flow






