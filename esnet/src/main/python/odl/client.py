import struct
from java.lang import Short
from java.util import LinkedList

from common.openflow import SimpleController
from common.utils import singleton

from org.opendaylight.controller.sal.core import Node

import net.es.netshell.odl.Controller

from org.opendaylight.controller.sal.match import Match
from org.opendaylight.controller.sal.match.MatchType import DL_DST
from org.opendaylight.controller.sal.match.MatchType import DL_SRC
from org.opendaylight.controller.sal.match.MatchType import DL_VLAN
from org.opendaylight.controller.sal.match.MatchType import IN_PORT


from org.opendaylight.controller.sal.action import Output
from org.opendaylight.controller.sal.action import SetDlDst
from org.opendaylight.controller.sal.action import SetDlSrc
from org.opendaylight.controller.sal.action import PopVlan
from org.opendaylight.controller.sal.action import PushVlan

from org.opendaylight.controller.sal.flowprogrammer import Flow

class ODLClient(SimpleController):
    """
    Class that is an interface to the ENOS OpenDaylight client.
    The real client functionality is the net.es.netshell.odl.Controller
    class (in Java).
    """

    def __init__(self):
        self.__class__ = SimpleController
        #super(ODLClient,self).__init__()
        SimpleController.__init__(self)
        self.__class__ = ODLClient
        self.odlController = net.es.netshell.odl.Controller.getInstance()

    def makeODLFlowEntry(self, flowMod, odlNode):
        """
        Given a FlowMod object, turn it into a Flow suitable for passing to ODL.

        Encapsulates a bunch of common sense about the order in which flow actions
        should be applied.

        :param flowMod: ENOS FlowMod
        :param odlNode: OpenDaylight Node object
        :return:
        """

        # Compose match object                                                     `
        match = Match()
        if 'in_port' in flowMod.match.props:
            # Compose the port name
            portname = flowMod.switch.props['mininetName'] + '-' + flowMod.match.props['in_port'].name
            nodeconn = self.odlController.getNodeConnector(odlNode, portName)
            match.setField(IN_PORT, nodeconn)
        if 'dl_src' in flowMod.match.props:
            match.setField(DL_SRC, flowMod.match.props['dl_src'])
        if 'dl_dst' in flowMod.match.props:
            match.setField(DL_DST, flowMod.match.props['dl_dst'])
        if 'vlan' in flowMod.match.props:
            match.setField(DL_VLAN, Short(flowMod.match.props['vlan']))

        # Compose action.
        # We do the data-link and VLAN translations first.  Other types of
        # translations would happen here as well.  Then any action to forward
        # packets.
        actionList = LinkedList()

        # Current code assumes there is only one action
        action = flowMod.actions[0]
        if 'dl_dst' in action.props:
            actionList.add(SetDlDst(action.props['dl_dst']))
        if 'dl_src' in action.props:
            actionList.add(SetDlSrc(action.props['dl_src']))
        if 'vlan' in action.props:
            actionList.add(PushVlan(action.props['vlan']))
        if 'out_port' in action.props:
            val = action.props['out_port']
            if val != None:
                for p in val:
                    # Compose the port name, which comes from the mininet switch name ("s2") and our
                    # port name ("eth1").  We then need to look this up in the ODL SwitchManager,
                    # but that requires a pointer to the ODL Node.
                    portName = flowMod.switch.props['mininetName'] + "-" + p.name
                    nodeconn = self.odlController.getNodeConnector(odlNode, portName)
                    actionList.add(Output(nodeconn))

        # compose flow
        flow = Flow(match, actionList)
        return flow

    def addFlowMod(self, flowMod):
        """
        Implementation of addFlowMod for use with OpenDaylight.
        Uses the net.es.netshell.odl.Controller.
        :param flowMod:
        :return:
        """
        # check scope
        if self.isFlowModValid(flowMod):
            # Given the switch in the ENOS (Python) world, find the switch in the
            # ODL (Java) world.  We basically have to iterate over all of the switches
            # the controller knows about and match on the DPID.  This stupidity is
            # because there's apparently no way in the SwitchManager API to search for a
            # switch by its name or DPID.
            # XXX I bet this operation is expensive.  Maybe we should think about putting in
            # a one-deep cache of the switch lookup.
            switches = self.odlController.getNetworkDevices()
            sw = None
            # Its seems that ODL returns 6 bytes DPID instead of 8.
            dpid = flowMod.switch.props['dpid'][-6:]
            for s in switches:
                # Find the switch that has the same DPID as the one we want to talk to.
                # Note that we also have the mininet switch name in flowMod.switch.props['mininetName']
                if s.dataLayerAddress == dpid: # Representation of DPID?
                    sw = s
                    break
            if sw == None:
                return False

            flow = self.makeODLFlowEntry(flowMod, sw.node)
            # go to the controller
            self.odlController.addFlow(sw.node, flow)

            # get result
            return True
        return False


    def send(self,packet):
        # to be implemented
        if self.isPacketOutValid(packet):
            print "PACKET_OUT:",packet
            return True
        return False

    def delFlowMod(self, flowMod):

        return False

# Creates an instance of ODLClient
instance = ODLClient()
def getODLClient():
    return instance

