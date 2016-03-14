#!/usr/bin/python
#
# ESnet Network Operating System (ENOS) Copyright (c) 2015, The Regents
# of the University of California, through Lawrence Berkeley National
# Laboratory (subject to receipt of any required approvals from the
# U.S. Dept. of Energy).  All rights reserved.
#
# If you have questions about your rights to use or distribute this
# software, please contact Berkeley Lab's Innovation & Partnerships
# Office at IPO@lbl.gov.
#
# NOTICE.  This Software was developed under funding from the
# U.S. Department of Energy and the U.S. Government consequently retains
# certain rights. As such, the U.S. Government has been granted for
# itself and others acting on its behalf a paid-up, nonexclusive,
# irrevocable, worldwide license in the Software to reproduce,
# distribute copies to the public, prepare derivative works, and perform
# publicly and display publicly, and to permit other to do so.
#


from net.es.netshell.api import Container,Node,Port,Link

def createtopo(topology):
    container = Container.createContainer(topology)

def deletetopo(topology):
    container = Container.getContainer(topology)
    if container != None:
        container.deleteContainer()

def addnode(topology,nodename):
    container = Container.getContainer(topology)
    if container == None:
        print topology,"does not exist."
        return False
    node = Node(nodename)
    node.properties['Ports'] = {}
    container.saveResource(node)
    return True

def delnode(topology,nodename):
    container = Container.getContainer(topology)
    if container == None:
        print topology,"does not exist."
        return False
    node = container.loadResource(nodename)
    if node == None:
        print nodename,"does not exist"
        return False
    node.delete(container)
    return True

def addlink(topology,linkname,srcnodename,dstnodename,both=False):
    container = Container.getContainer(topology)
    if container == None:
        print topology,"does not exist."
        return False
    srcnode = container.loadResource(srcnodename)
    if srcnode == None:
        print srcnodename,"does not exist"
        return False
    dstnode = container.loadResource(dstnodename)
    if dstnode == None:
        print dstnodename,"does not exist"
        return False
    link = Link(linkname + "-" + srcnodename + "-" + dstnodename)
    srcport = Port(srcnodename + "-" + link.getResourceName())
    srcport.properties['Link'] = link.getResourceName()
    srcport.properties['Node'] = srcnodename
    srcnode.properties['Ports'][srcport.getResourceName()] = srcport.getEid()
    dstport = Port(dstnodename + "-" + link.getResourceName())
    dstport.properties['Link'] = link.getResourceName()
    dstnode.properties['Ports'][dstport.getResourceName()]= dstport.getEid()
    link.properties['SrcPort'] = srcnodename
    link.properties['DstPort'] = dstnodename
    link.setWeight(1) # default
    container.saveResource(link)
    container.saveResource(srcport)
    container.saveResource(dstport)
    if both:
        link = Link(linkname + "-" + dstnodename + "-" + srcnodename)
        srcport = Port(dstnodename + "-" + link.getResourceName())
        srcport.properties['Link'] = link.getResourceName()
        srcnode.properties['Ports'][dstport.getResourceName()] = dstport.getEid()
        dstport = Port(srcnodename + "-" + link.getResourceName())
        dstport.properties['Link'] = link.getResourceName()
        dstnode.properties['Ports'][srcport.getResourceName()] = srcport.getEid()
        link.properties['SrcPort'] = dstnodename
        link.properties['DstPort'] = srcnodename
        link.setWeight(1) # default
        container.saveResource(link)
        container.saveResource(srcport)
        container.saveResource(dstport)
    container.saveResource(srcnode)
    container.saveResource(dstnode)
    return True

def dellink(topology,linkname,srcnodename,dstnodename,both=False):
    container = Container.getContainer(topology)
    if container == None:
        print topology,"does not exist."
        return False
    srcnode = container.loadResource(srcnodename)
    if srcnode == None:
        print srcnodename,"does not exist"
        return False
    dstnode = container.loadResource(dstnodename)
    if dstnode == None:
        print dstnodename,"does not exist"
        return False
    link = container.loadResource(linkname + "-" + srcnodename + "-" + dstnodename)
    if link == None:
        print linkname,"does not exist"
        return False
    srcport = container.loadResource(srcnodename + "-" + link.getResourceName())
    if srcport == None:
        print "link port does not exist"
        return False
    srcport.properties['Link'] = link.getResourceName()
    srcport.properties['Node'] = srcnodename
    srcnode.properties['Ports'][srcport.getResourceName()] = srcport.getEid()
    dstport = container.loadResource(dstnodename + "-" + link.getResourceName())
    if dstport == None:
        print "link port does not exist"
        return False
    dstport.properties['Link'] = link.getResourceName()
    dstnode.properties['Ports'][dstport.getResourceName()]= dstport.getEid()
    link.properties['SrcPort'] = srcnodename
    link.properties['DstPort'] = dstnodename
    link.setWeight(1) # default
    container.saveResource(link)
    container.saveResource(srcport)
    container.saveResource(dstport)
    if both:
        link = Link(linkname + "-" + dstnodename + "-" + srcnodename)
        srcport = Port(dstnodename + "-" + link.getResourceName())
        srcport.properties['Link'] = link.getResourceName()
        srcnode.properties['Ports'][dstport.getResourceName()] = dstport.getEid()
        dstport = Port(srcnodename + "-" + link.getResourceName())
        dstport.properties['Link'] = link.getResourceName()
        dstnode.properties['Ports'][srcport.getResourceName()] = srcport.getEid()
        link.properties['SrcPort'] = dstnodename
        link.properties['DstPort'] = srcnodename
        link.setWeight(1) # default
        container.saveResource(link)
        container.saveResource(srcport)
        container.saveResource(dstport)
    container.saveResource(srcnode)
    container.saveResource(dstnode)
    return True

def print_syntax():
    print
    print "topoctl <cmd> <cmds options>"
    print "topoctl <toplogy> <cmd> <cmds options>"
    print "Manipulates generic topologies."
    print " Commands are:"
    print "\thelp"
    print "\t\tPrints this help."
    print "\tcreate <topology name>"
    print "\t\tcreates a new topology."
    print "\tdelete <topology name>"
    print "\t\tdeletes a new topology."
    print "\t<topology> add-node <node name>:"
    print "\t\t adds a node in the topology."
    print "\t<toploogy> del-node <node name>:"
    print "\t\t deletes a node in the topology."
    print "\t<toploogy> add-link <link name> <src> <dst> [both]:"
    print"\t\tCreates a link between two nodes of the topology. If the option both is provided,"
    print"\t\tthe opposite links is automatically added."
    print "\t<toploogy> del-link <link name> <src> <dst> [both]:"
    print"\t\tDeletes a link between two nodes of the topology. If the option both is provided,"
    print"\t\tthe opposite links is automatically deleted."

if __name__ == '__main__':
    argv = sys.argv

    if len(argv) == 1:
        print_syntax()
        sys.exit()
    cmd = argv[1]
    if cmd == "help":
        print_syntax()
    elif cmd == "create":
        topology = argv[2]
        createtopo (topology)
    elif cmd == "delete":
        topology = argv[2]
        deletetopo (topology)
    else:
        topology = argv[1]
        cmd = argv[2]
        if cmd  == "add-node":
            nodename = argv[3]
            addnode(topology,nodename)
        elif cmd == "del-node":
            nodename = argv[3]
            delnode(topology,nodename)
        elif cmd == "add-link":
            linkname = argv[3]
            srcnodename = argv[4]
            dstnodename = argv[5]
            both = False
            if len(argv) > 6:
                if argv[6] == "both":
                    both = True
            addlink(topology,linkname,srcnodename,dstnodename,both)





