from mininet.sites import SiteIntent, SiteRenderer
from common.openflow import SimpleController
from mininet.enos import TestbedTopology
from mininet.l2vpn import SDNPopsRenderer,SDNPopsIntent
from mininet.wan import WanRenderer, WanIntent
from net.es.netshell.api import GenericGraphViewer

import copy

import random
from common.utils import InitLogger, dump
from mininet.mat import MAT

def getPop(topo,coreRouter):
    pops = topo.builder.pops
    for (x,pop) in pops.items():
        if pop.props['coreRouter'].name == coreRouter.name:
            return pop
    return None

intents = {}
renderers = {}
if __name__ == '__main__':
    random.seed(0)    # in order to get the same result to simplify debugging
    InitLogger()
    configFileName = None
    net=None
    intent=None
    if len(sys.argv) > 1:
        configFileName = sys.argv[1]
        net = TestbedTopology(fileName=configFileName)
    else:
        net = TestbedTopology()
    net1 = net
    # One-time setup for the VPN service
    wi = WanIntent("esnet", net.builder.pops)
    wr = WanRenderer(wi)
    wr.execute()
    rendererIndex = {} # [sitename] = SiteRenderer
    pops = [] # pops that contains a site
    allHosts = []
    allLinks = []
    for site in net.builder.sites:
        hosts = map(lambda h : h.props['enosNode'], site.props['hosts'])
        borderRouter = site.props['borderRouter'].props['enosNode']
        siteRouter = site.props['siteRouter'].props['enosNode']
        links = map(lambda l : l.props['enosLink'], site.props['links'])
        intent = SiteIntent(name=site.name, hosts=hosts, borderRouter=borderRouter, siteRouter=siteRouter, links=links)
        renderer = SiteRenderer(intent)
        err = renderer.execute()
        rendererIndex[site.name] = renderer
        pops.append(site.props['pop'])
        allHosts.append(siteRouter)
        allHosts.append(borderRouter)
        allHosts.extend(hosts)
        allLinks.extend(links)

    for vpn in net.builder.vpns:
        vpn.props['mat'] = MAT(vpn.props['vid'])
        popsIntent = SDNPopsIntent(name="vpn", vpn=vpn, topo=net.builder)
        popsRenderer = SDNPopsRenderer(popsIntent)
        popsRenderer.execute()
        lanVlan = vpn.props['lanVlan']
        for participant in vpn.props['participants']:
            (site, hosts, wanVlan) = participant
            siteRenderer = site.props['siteRouter'].props['toWanPort'].props['enosPort'].props['scope'].owner
            siteRenderer.addVpn(lanVlan, wanVlan)
        print "VPN " + vpn.name + " is up."
