/*
 * ESnet Network Operating System (ENOS) Copyright (c) 2015, The Regents
 * of the University of California, through Lawrence Berkeley National
 * Laboratory (subject to receipt of any required approvals from the
 * U.S. Dept. of Energy).  All rights reserved.
 *
 * If you have questions about your rights to use or distribute this
 * software, please contact Berkeley Lab's Innovation & Partnerships
 * Office at IPO@lbl.gov.
 *
 * NOTICE.  This Software was developed under funding from the
 * U.S. Department of Energy and the U.S. Government consequently retains
 * certain rights. As such, the U.S. Government has been granted for
 * itself and others acting on its behalf a paid-up, nonexclusive,
 * irrevocable, worldwide license in the Software to reproduce,
 * distribute copies to the public, prepare derivative works, and perform
 * publicly and display publicly, and to permit other to do so.
 */
package net.es.enos.esnet;

import net.es.netshell.api.Link;
import net.es.netshell.api.Node;
import net.es.netshell.api.Port;
import org.jgrapht.GraphPath;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;

/**
 * Created by lomax on 5/28/14.
 */
public class OSCARSReservations {

    private final Logger logger = LoggerFactory.getLogger(OSCARSReservations.class);
    private ESnetTopology topology;
    private List<ESnetCircuit> circuits;
    private HashMap<Link,Long> linksMaxReservable = new HashMap<Link, Long>();

    public class PortReservation {
        public long maxReservable;
        public long[] alreadyReserved = new long[2]; // Path forward and back
        public PortReservation (long maxReservable) {
            this.maxReservable = maxReservable;
        }
    }
    /**
     * Returns the list of ACTIVE or RESERVED OSCARS circuits.
     * @return  a list of circuits.
     * @throws IOException
     */
    public  List<ESnetCircuit> retrieveScheduledCircuits() throws IOException {
        OSCARSTopologyPublisher publisher = new OSCARSTopologyPublisher();
        ESnetJSONTopology jsonTopology = publisher.toJSON();
        return jsonTopology.getCircuits();
    }

    public OSCARSReservations(ESnetTopology topology) throws IOException {
        this.topology = topology;
        this.circuits = this.retrieveScheduledCircuits();
    }

    public long getMaxReservableBandwidth (GraphPath<Node,Link> path, DateTime start,DateTime end) throws IOException {

	    // First compute the aggregate reserved bandwidth on the overall topology
	    HashMap<ESnetPort, PortReservation> reserved = this.getReserved(start, end);

	    long maxReservable = -1;
	    long remainTo;
	    // Then compute max reservable for each link.
	    for (Link link : path.getEdgeList()) {
		    Port port = topology.getPortByLink(link.getResourceName());
		    reserved.get(port);
		    PortReservation portReservation = reserved.get(port);
		    if (portReservation == null) {
			    continue;
		    }
		    remainTo = portReservation.maxReservable - portReservation.alreadyReserved[0];
		    if (maxReservable == -1 || maxReservable > remainTo) {
			    maxReservable = remainTo;
		    }
	    }
	    return maxReservable;
    }

    /**
     * Reads all the reservations that are active within the specified time range and
     * aggregates, per port, the bandwidth that is already reserved. The method returns
     * the data in the form of HashMap of PortReservation, index by Port. PortReservation
     * contains both the reservation that has already been made and the maximum bandwidth
     * that is allowed on this port.
     * @param start time of the query
     * @param end time of the query
     * @return  an HashMap of PortReservation indexed by ESnetPort
     */
    public HashMap<ESnetPort, PortReservation> getReserved (DateTime start, DateTime end) {
        OSCARSTopologyPublisher publisher = new OSCARSTopologyPublisher();
        ESnetJSONTopology jsonTopology = publisher.toJSON();

        HashMap<String,Link> links = topology.getLinks();
        HashMap<ESnetPort,PortReservation> reserved = new HashMap<ESnetPort, PortReservation>();
        List<ESnetCircuit> reservations = jsonTopology.getCircuits();

	    // Initialize all ports with their maximum reservable capacity.
		for (Link tempLink : links.values()){
			ESnetLink link = (ESnetLink) tempLink;
			ESnetPort port = topology.getPortByLink(link.getId());
            PortReservation portReservation = null;
            if (port == null) {
                // TODO: lomax@es.net should perhaps do better.
                continue;
            }
            if (port.getMaximumReservableCapacity() == null) {
                portReservation = new PortReservation(0L);
            }  else {
			    portReservation =
					new PortReservation(Long.parseLong(port.getMaximumReservableCapacity()));
            }
			reserved.put(port, portReservation);
		}

        for (ESnetCircuit reservation : reservations) {
            if (! reservation.isActive(start,end))  {
                // This reservation is not active withing the query time frame, ignore
                continue;
            }
            List<ESnetSegment> segments = reservation.getSegments();
            int segmentCounter = 0;
            for (ESnetSegment segment : segments) {
                List<String> portNames = segment.getPorts();
                for (String portName : portNames) {
                    // Remove the VLAN off the port name, if any.
                    String[] tmp = portName.split(":");
                    String[] tmp2 = tmp[5].split(".");
                    if (tmp[5].indexOf(".") > 0) {
                        tmp[5] = tmp[5].substring(0,tmp[5].indexOf("."));
                        continue;
                    }
                    portName = "";
                    for (String s : tmp) {
                        portName += s + ":";
                    }
                    portName = portName.substring(0,portName.length() -1);

                    // Retrieve port from topology.
                    ESnetLink link = topology.searchLink(portName);
                    if (link == null) {
                        // This is a link to another domain
                        continue;
                    }
                    Port p = topology.getPortByLink(link.getId());
                    if (p == null) {
                        throw new RuntimeException("No port in topology that matches OSCARS path element " + portName);
                        // TODO: lomax@es.net perhaps should do something better
                        //continue;
                    }
                    if ( ! (p instanceof ESnetPort)) {
                        // This implementation relies on ESnet types
                        throw new RuntimeException("Unexpected type " + p.getClass().getCanonicalName());
                    }
                    ESnetPort port = (ESnetPort) p;
                    if (reserved.containsKey(port)) {
                        PortReservation portReservation = reserved.get(port);

                        portReservation.alreadyReserved[segmentCounter] = portReservation.alreadyReserved[segmentCounter]
                                                            + Long.parseLong(reservation.getCapacity());

                    } else {
                        // First time this port is seen. Create a PortReservation
                        PortReservation portReservation =
                                new PortReservation(Long.parseLong(port.getMaximumReservableCapacity()));
                        portReservation.alreadyReserved[segmentCounter] = Long.parseLong(reservation.getCapacity());
                        reserved.put(port, portReservation);
                    }
                }
                ++segmentCounter;
            }
        }
        return reserved;
    }
}
