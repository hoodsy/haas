#HaaS API

Eventually this will be the final documentation for the API, for now,
it has additional information to give context for the conversation.
We first discuss the original API, then the proposed API.

##Original API
Current interface, grew organically:

    group create <group_name>
    node create <node_id>
    node add <node_id> <group_name>
    nic create <nic_id> <mac_addr> <name>
    nic connect <nic_id> <port_id>
    nic add <nic_id> <node_id>
    switch create <switch_id> <script>
    port create <port_id> <switch_id> <port_no>
    vlan create <vlan_id>
    vlan connect <vlan_id> <group_name> <nic_name>
    headnode create
    headnode attach <vm_name> <group_name>
    group deploy <group_name>
    user create <user name> <password>
    show all
    show [ group | vm | port | nic | vlan | switch | node | user ]
    help
    exit

Not clear what was atomic, synchronization model, and there were a
series of inconsistencies, and we don't have model of permissions...

##Proposed API

First describe the main objects, the users and security model, then
then the actual API.

###Objects on the (new model) are:

* user - a user, with password and login, can belong to multiple groups
* group - owner of a set of projects, has zero or more users in the
  group. 
* project - a grouping of resources (e.g., headnode, set of nodes,
  networks). Owned by a single group. 
* node - a physical node, can be free or in one and only one
  project. Has one or more  NICs attached to it.   
* headnode   - a controlling machine for a project, today a VM, assigned
  to one project  
* NIC - network card, identified by a user-specified label (e.g.,
  PXE, ipmi, user1, silly) will have a visible ethernet mac address
  (or equivalent unique number for other network types), and is always
  part of one node and connected to at most one port.
* HNIC - headnode network card, identified by a user-specified label (e.g.,
  PXE, ipmi, user1, silly) will have a visible ethernet mac address
  (or equivalent unique number for other network types), and is always
  part of one headnode.
* switch - a physical network switch, note not visible to
  users, just admins, has one or more ports
* port - a port on a switch to which NICs can be connected.
  Note, not visible to users, just to admins 
* network - a network, today implemented as a VLAN, will be in one or
  more projects.  

While we expect certain relationships between objects, e.g., one
headnode per project, we do not perform any actions to enforce this
relationship.  We expect users to configure the components above in
relationships we don't anticipate today.  As a result, we do not, for
example, provide garbage collection of orphaned objects, ... it is
assumed that its users are sophisticated, and tools are built above
the HaaS service to keep users from shooting themselves in the foot.
For example, the HaaS layer won't, when a group frees a node, remove
it from all the group's networks.  Similarly we won't when deleting a
project, in turn free the nodes and delete the headnodes.  It will be
the user/higher level tools' responsibility.  

Most objects are identified by "labels" that are globally unique,
e.g., nodes, networks, groups, users, headnodes.  While we may
eventually change this, it seems a reasonable limitation for now that
simplifies the implementation and will allow potential sharing of
resources. The system will return an error if a second user tries to
create an object with an already existing label. The one exception is
NICs, where the label is unique only on a per-node basis. 

### Permissions users and synchronization mechanisms/assumptions

Users will belong to one or more groups that own projects.  One
special group is the "admin" group that: 1) is responsible for
configuring the system and adding physical capacity, and 2) can create
new groups, and remove resources from misbehaving groups...

The only user visible objects that can be shared between groups are
networks and users. 

To allow the administrators to modify the system resources without
messing up users trying to access the system concurrently, the HaaS
allows administrators to "block" any user not belonging to the admin
group from the system. Administrators are expected to coordinate among
themselves to ensure that only one is reconfiguring the system at a
time. 

To ensure users to be able to configure their systems in a fashion
where "their" users see a complete set of changes, rather than
intermediate results, we provide a "deploy" operation, where users can
make many individual changes, and then "deploy" them in one operation to
the network.  Users are expected to coordinate among themselves on
changes to a project so that two users are not modifying the same
project at the same time. 


###User operations:
    user_create                 <user_label> <password>
    user_destroy                <user_label>
 
    group_add_user              <group_label> <user_label> 
    group_add_network           <group_label> <network_label> 

    project_create              <project_label> <group_label>
    project_destroy             <project_label>
 
    # create and destroy logical networks
    network_create              <network_label> <group_label>
    network_destroy             <network_label>
 
    headnode_create             <hn_label> <group_label>
    headnode_destroy            <hn_label>
    project_connect_headnode    <hn_label> <project_label>
    project_detach_headnode     <hn_label> <project_label>
 
    # allocate/deallocate node to a project
    project_connect_node        <project_label> <node_label> 
    project_detach_node         <project_label> <node_label> 
 
    # networking operations on a project
    project_connect_network     <project_label> <network_label>
    project_detach_network      <project_label> <network_label>
    project deploy              <project_label>
 
    # networking operations on a physical node
    node_connect_network        <node_label> <nic_label> <network_label>
    node_detach_network         <node_label> <nic_label> 
 
    # networking operations on a headnode
    headnode_create_hnic        <hn_label> <hnic_label> 
    headnode_destroy_hnic       <hn_label> <hnic_label>
    headnode_connect_network    <hn_label> <hnic_label> <network>
    headnode_detach_network     <hn_label> <hnic_label> 
 
    # query interface, limited for users to resources 
    # that are free, or that groups belonging to user own
    show [ group | project | vm | port | nic | hnic | vlan | switch |
      node | user ] <obj> 
    help
    exit

###Additional administrator operations:

    # operations to describe physical configuration of system to HaaS
    node_create                 <node_label>
    node_destroy                <node_label>
    node_create_nic             <node_label> <nic_label> <mac_addr>
    node_destroy_nic            <node_label> <nic_label> 
    switch_create               <switch_label> <script> <number_ports>
    switch_destroy              <switch_label> 
    nic_connect_switch          <node_label> <nic_label> <switch_label> <port>
 
    # dump all information about the system
    show all

    #import a vlan (e.g., public VLAN) into the system
    import_vlan <network_label> <vlan_id>

    # block and unblock users without admin privileges
    block_users
    unblock_users


###Summary of Changes

* added concepts of projects AND groups, one for users, other for all other
  resources
* all create operations of logical entities assign them to a group. 
* commands start with the name of the containing object
  e.g., node add -> group connect node 
* consistent naming, i.e., connect/disconnect rather than
  attach/add/...
* vlan -> network
* hide internal numbers, e.g. vlan_id, ... instead use lables
* got rid of operations on group of objects, i.e., vlan connect
  operated on all nics with label, which would have forced us to do
  bizzare work if a new nic got added with same label
* connect all words in command with "_" since could be function name
* headnode create specifies a vm_label
* call string names everywhere
* got rid port_id and port_no, always identify port as a switch and
  port number relative to that switch, like nics on a node
* give access to networks, attach things, ... by "connect" operations,
  e.g. connect a network to a group, connect a nic to a port, connect
  a nic to a network, connect a user to a group

###Notes:
* network has to be connected to a group before it can be connected 
  to a node in the group, i.e, an group A can give group B access to
  network, group B users can then connect network to nodes in their group
* should it be `node_connect_network` or `network_connect_node`?
* how do we associate arbitrary data with an object, e.g., mac
  address... we should have operations to get info about an arbitrary
  object 
* user_destroy will fail if the user is in any groups.  So, a user can
  create another user, add them to her groups, and then remove them and
  destroy them if they have not yet been added to other groups.  
* Note, the current model is that all users on a group have full
  control.  This seems sufficient for this simple tool, but we
  probably will need to revise in the longer term, as we want group
  administrators...
* When you create a headnode, you pass it an authorized_key files for
  the group, so user can log into it.  You also pass its own
  credentials so  that it can query the service. Each node will have
  its own credentials, and adding a headnode to a project will also,
  implicitly, add the headnode's credentials to that group. The user
  can move the headnode from one project to another, so the headnode
  needs to query the service to find out what project/... its
  connected to. The one piece   of information it has is the mac
  address of the nics it has. 
* right now we are working with ethernet and VLANs, and in a few
  places this is visible.  We will need to reconsider some of the
  interfaces when we move to IB and/or SDN
