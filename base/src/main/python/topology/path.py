from org.jgrapht.alg import DijkstraShortestPath
from net.es.enos.api import TopologyFactory
from net.es.enos.esnet import ESnetTopology,OSCARSReservations
from org.joda.time import DateTime

print "Starting"

topology = TopologyFactory.instance()
topo = topology.retrieveTopologyProvider("localLayer2")

graph = topo.retrieveTopology()
nodes = topo.getNodes()
nodesByLink = topo.getNodesByLink()
portsByLink = topo.getPortsByLink()

srcNode = nodes.get("urn:ogf:network:es.net:lbl-mr2")
dstNode = nodes.get("urn:ogf:network:es.net:bnl-mr3")

path = DijkstraShortestPath.findPathBetween(graph, srcNode, dstNode)


start = DateTime.now()
end = start.plusHours(2)
reserved = OSCARSReservations().getReserved(start,end)

print "Start Node= " + srcNode.getId()

for link in path:
        nodes = nodesByLink.get(link)
	ports = portsByLink.get(link)
	port = ports[0] # Assume only one port per link
	portReservation = reserved.get(port)
	if portReservation == None:
		print "No portReservation for link " + link.getId() + " port= " +  "   " + port.getId()
		continue
	remainTo = portReservation.maxReservable - portReservation.alreadyReserved[0]
	remainFrom = portReservation.maxReservable - portReservation.alreadyReserved[1]
        print "Node= " + nodes[0].getId() + "\tlinkId= " + link.getId() + "\tReservableTo= " + remainTo + "\tReservableFrom= " + remainFrom


print "End Node= " + dstNode.getId()

for p in reserved.keySet():
	pr = reserved.get(p)
	print p.getId() + " " + str(pr.maxReservable)	


