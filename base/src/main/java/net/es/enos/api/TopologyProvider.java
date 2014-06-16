/*
 * Copyright (c) 2014, Regents of the University of California  All rights reserved.
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package net.es.enos.api;

import net.es.enos.esnet.ESnetLink;
import net.es.enos.esnet.ESnetNode;
import org.jgrapht.graph.ListenableDirectedGraph;
import org.jgrapht.graph.ListenableDirectedWeightedGraph;
import org.joda.time.DateTime;

import java.io.IOException;
import java.util.List;
import java.util.HashMap;


/**
 * Created by lomax on 5/21/14.
 */
public abstract class TopologyProvider {

    public static enum WeightType {
                                   TrafficEngineering, // Path cost as defined by ESnet NESG
                                   MaxBandwidth,       // Maximum reservable bandwidth by OSCARS
    }

    /**
     * Convenience method computing the path start now and ending one minute later, meaning, right now.
     * @param weight
     * @return
     * @throws IOException
     */
    public ListenableDirectedWeightedGraph<ESnetNode, ESnetLink> getGraph(WeightType weight) throws IOException {
        DateTime start = DateTime.now();
        DateTime end = start.plusMinutes(1);
        return this.getGraph(start, end,weight);
    }

    public ListenableDirectedWeightedGraph<ESnetNode, ESnetLink> getGraph(DateTime start,
                                                                          DateTime end,
                                                                          WeightType weightType) throws IOException {
        return null;
    }

    public HashMap<String, ESnetNode> getNodes() {
        return null;
    }

    /**
     * Returns a HashMap of List of Links that connects to or from a Site to this topology. The map is indexed by
     * the name of the site as found in the topology.
     *
     * @return returns the indexed Map.
     */
    public HashMap<String, List<Link>> getSiteLinks() {
        return null;
    }

    /**
     * Returns a HashMap of List of Links that connects to or from another Domain to this topology. The map is indexed by
     * the name of the domain as found in the topology.
     *
     * @return returns the indexed Map.
     */
    public HashMap<String, List<Link>> getPeeringLinks() {
        return null;
    }

    /**
     * Returns a HashMap of List of Links that connects two Nodes of this topology. The map is indexed by
     * the name of the node as found in the topology.
     *
     * @return returns the indexed Map.
     */
    public HashMap<String, List<Link>> getInternalLinks() {
        return null;
    }

    /**
     * Returns a HashMap of List of Nodes indexed by Link. When links are directional, the source Node is indexed.
     *
     * @return a HashMap of Lists of Nodes.
     */
    public HashMap<Link, List<Node>> getNodesByLink() {
        return null;
    }

    /**
     * Returns a HashMap of List of Ports indexed by Link. When links are directional, the source Port is indexed.
     *
     * @return a HashMap of Lists of Ports.
     */
    public HashMap<Link, List<Port>> getPortsByLink() {
        return null;
    }

    /**
     * Retrieve from the topology the Node object referenced by its name. The format of the name is as follow:
     * host@domain. For instance, lbl-mr2@es.net. Note that the implementation of the topology may have a
     * different format to identify the nodes: the Node id, as retrieved with Node.getId() is an opaque.
     *
     * @param name is the abstract name of the node, formatted as hostname@domain.
     * @return the node object if any, of the node identified by name.
     */
    public Node getNode(String name) {
        return null;
    }
}
