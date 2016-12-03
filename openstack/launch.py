"""
   file: launch.py
   vers: 1.8
   desc: Openstack Tor Network builder backend
"""

import time
import getpass
import logging
from novaclient.client import Client

debug_on = False
num_nodes = 0

# Logging functions

def logger(session, alert, bug, err):
    timestamp = time.strftime("%m%d%Y")
    logtime = time.strftime(" %H:%M.%S ")
    fn = "tor_net_" + timestamp + ".log"
    logging.basicConfig(filename=fn, filemode='a', level=logging.DEBUG)
    """
       TODO: implement
    """
    if alert is not None:
        logging.warn(logtime + alert)
    if session is not None:
        logging.info(logtime + session)
    if bug is not None:
        if debug_on:
            logging.debug(logtime + bug)
    if err is not None:
        logging.error(logtime + err)

# Connection functions

def get_auth(username, password):
    """
       TODO: remove hardcoded variables

       Dictionary for user authentication parameters

       Function of:
           create_novaclient
           create_neutronclient

       Args:
           username - RIT DCE username
           password - RIT DCE password

       Returns:
           auth - dictionary for authenticating to openstack keyauth
    """
    username = username + "@ad.rit.edu"
    auth = {}
    auth['version'] = '2'
    auth['insecure'] = True
    auth['username'] = username
    auth['password'] = password
    auth['auth_url'] = 'https://acopenstack.rit.edu:5000/v2.0'
    auth['project_id'] = 'jrh7130-multi'
    if auth['insecure'] == True:
        cert_warn = "Connection: SSL certificates being ignored"
        logger(None, cert_warn, cert_warn, None)
    return auth

def toggle_debug():
    global debug_on
    if not debug_on:
        debug_on = True
        print("Debugging on, see log file")
    else:
        debug_on = False
        print("Debugging off")

# Network config functions

def create_novaclient(username,password):
    """
        Creates a nova client with given authentication parameters

        Function of:
           main
           web_launch
           
        Args:
           none

        Returns:
           nova_client - object to query openstack
    """
    if username is None:
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        logger("Nova client initialized by " + username + " from command line",None,None,None)
    auth = get_auth(username,password)
    nova_client = Client(**auth)
    return nova_client

# List functions

def list_hub(nova_client):
    """
       Menu for reporting related functions

       Function of:
          main
    """
    while(True):
        print("\nBackend Reporting Functions")
        print("1. List Instances")
        print("2. List Images")
        print("3. List Flavors")
        print("4. List Networks")
        print("5. Return to Main Menu")
        try:
            case = int(input("Enter choice: "))
        except:
            case = 6
        if case == 1:
            list_instances(nova_client)
        elif case == 2:
            list_images(nova_client)
        elif case == 3:
            list_flavors(nova_client)
        elif case ==4:
            list_networks(nova_client)
        elif case == 5:
            return
        else:
            print("\nInvalid option")

def list_instances(nova_client):
    """
       Lists available instances

       Args:
           client - nova client object

       Returns:
           none
    """
    print("\nList Instances: ")
    for line in nova_client.servers.list():
        print(line)

def list_images(nova_client):
    """
       Lists available images

       Args:
           client - nova client object

        Returns:
            none
    """
    print("\nList Images: ")
    for line in nova_client.images.list():
        print(line)

def list_flavors(nova_client):
    """
       Lists available flavors

       Args:
           client - nova client object

        Returns:
            none
    """
    print("\nList Flavors: ")
    for line in nova_client.flavors.list():
        print(line)

def list_networks(nova_client):
    """
       Lists available networks

       Args:
           client - nova client object

        Returns:
            nets - a list of networks
    """
    print("\nList Networks: ")
    nets = []
    for line in nova_client.networks.list():
        print(line)
        nets.append(line)
    return nets

# Instance functions

def instance_hub(nova_client):
    """
       Menu for instance related functions
    """
    while(True):
        print("\nBackend Instance Functions")
        print("1. Create Instance")
        print("2. Terminate Instance")
        print("3. Rename Instance")
        print("4. Return to Main Menu")
        try:
            case = int(input("Enter choice: "))
        except:
            case = 6
        if case == 1:
            create_instance(nova_client)
        elif case == 2:
            terminate_instance(nova_client)
        elif case == 3:
            rename_instance(nova_client)
        elif case == 4:
            return
        else:
            print("\nInvalid option")
    

def create_instance(nova_client):
    """
       Creates an instance of given name, image and flavor

       Args:
           name_in - name of new instance
           img_in - name of image to use
           flav_in - name of flavor to use

        Returns:
            none
    """
    try:
        name_in = input("Enter instance name: ")
        img_in = input("Enter image to use: ")
        image = nova_client.images.find(name=img_in)
        flav_in = input("Enter flavor: ")
        flavor = nova_client.flavors.find(name=flav_in)
        net = nova_client.networks.find(label="Shared")
        nics = [{'net-id': net.id}]
        instance = nova_client.servers.create(name=name_in,
                                              image=image,
                                              flavor=flavor,
                                              nics=nics)
        time.sleep(5)
    finally:
        print("Instance Created")

def terminate_instance(nova_client):
    """
       Terminates an instance of given name

       Args:
          name_in - name of instance to terminate

       Returns:
          None
    """
    servers_list = nova_client.servers.list()
    name_in = input("Enter instance name: ")
    server_exists = False

    for s in servers_list:
        if s.name == name_in:
            server_exists = True
            break
    if not server_exists:
        print("%s does not exist" % name_in)
    else:
        print("Deleting %s" % name_in)
        nova_client.servers.delete(s)

def rename_instance(nova_client):
    """
       TODO: implement

       Renames an existing instance of given name with new name

       Args:
          name_in - name of existing instance
          new_name - new name for instance

       Returns:
          None
    """
    servers_list = nova_client.servers.list()
    name_in = input("Enter instance name: ")
    server_exists = False

    for s in servers_list:
        if s.name == name_in:
            server = nova_client.servers.get(s.id)
            server_exists = True
            break
    if not server_exists:
        print("%s does not exist" % name_in)
    else:
        print("Renaming %s" % name_in)
        new_name = input("Enter new name for instance: ")
        server.update(server=new_name)

# Web functions

def create_utilserv(nova_client, util_config):
    util_config['name'] = "util_serv"
    util_config['size'] = 1
    global num_nodes
    num_nodes = num_nodes - 1
    util_list = create_node(nova_client, util_config)
    return util_list

def create_dirauth(nova_client, da_config):
    da_config['name'] = "dir_auth"
    da_config['size'] = da_config['da_size']
    da_config['script'] = "deploy.sh"
    global num_nodes
    num_nodes = num_nodes - da_config['da_size']
    da_list = create_node(nova_client,da_config)
    return da_list

def create_exitnode(nova_client, exit_config):
    exit_config['name'] = "exit_node"
    exit_config['script'] = "deploy.sh"
    global num_nodes
    n_size = int(num_nodes / 3)
    num_nodes = num_nodes - n_size
    exit_config['size'] = n_size
    exit_list = create_node(nova_client,exit_config)
    return exit_list

def create_relaynode(nova_client, relay_config):
    relay_config['name'] = "relay_node"
    relay_config['script'] = "deploy.sh"
    global num_nodes
    n_size = int(num_nodes / 2)
    num_nodes = num_nodes - n_size
    relay_config['size'] = n_size
    relay_list = create_node(nova_client,relay_config)
    return relay_list

def create_clientnode(nova_client, client_config):
    client_config['name'] = "client_node"
    client_config['script'] = "deploy.sh"
    global num_nodes
    n_size = int(num_nodes)
    num_nodes = num_nodes - n_size
    if num_nodes > 0:
        n_size = n_size + 1
        print(num_nodes)
    client_config['size'] = n_size
    client_list = create_node(nova_client,client_config)
    return client_list

def create_node(nova_client, config):
    """
        TODO: add error checking

        Helper function to create instances.

        Args:
            nova_client - instance of the client connection to Openstack
            config - dictionary containing parameters:
                        * image - name of image to use
                        * flavor - name of flavor to use
                        * netname - name of network to use
                        * modifier - name of launch script to use
                        * size - number of elements to create

        Returns:
            client_list - a list of client objects created
    """
    node_list = []
    image = config['image']
    flavor = config['flavor']
    netname = config['netname']
    deploy_script = config['script']
    size = config['size']
    node_name = config['name']
    util_ip = config['util_ip']

    if image is None:
        image = nova_client.images.find(name="Ubuntu 16.04 LTS")
    if flavor is None:
        flavor = nova_client.flavors.find(name="m1.tiny")
    if netname is None:
        netname = nova_client.networks.find(label="Shared")
    nics = [{'net-id': netname.id}]

    for i in range(0,size):
        name = node_name + str(i)
        instance = nova_client.servers.create(name=name,
                                              image=image,
                                              flavor=flavor,
                                              nics=nics,
                                              userdata=deploy_script)
        node_list.append(instance)
        time.sleep(5)
        logger(None,"Network: " + name + " node created",None,None)

    return node_list

# Teardown functions

def destroy_network(nova_client, node_list):
    """
	   TODO: Determine paramters to base deletion on
	"""
    for key in node_list:
        for e in node_list[key]:
            nova_client.servers.delete(e.id)
    
# Launch functions

def web_launch(nova_client, img, flav, netname, util_ip, size, da_size):
    """
        Called directly from the web interface. Creates nodes in the correct order
        and returns a list of new nodes ot the web interface.

        Args:
            nova_client - instance of Openstack Nova client object
            netname - name of network to use
            util_ip - IP address of the utility server
            size - size of network to create
            da_size - number of directory authorities to create

        Returns:
            nodes - a dictionary of lists containing the newly created nodes
    """
    logger("Nova client initialized by " + username + " from web UI",None,None,None)
    logger("Starting new network build of size " + str(size),None,None,None)
    
    config = {'image': img,
	      'flavor': flav,
	      'netname': netname,
	      'util_ip': util_ip,
	      'size': size,
              'da_size': da_size}

    global num_nodes
    num_nodes = config['size']

    da_list = create_dirauth(nova_client, config)
    exit_list = create_exitnode(nova_client, config)
    relay_list = create_relaynode(nova_client, config)
    client_list = create_clientnode(nova_client, config)
        
    nodes = {'client': client_list,
             'relay': relay_list,
             'exit': exit_list,
             'da': da_list}
    
    return nodes

def web_dismantle(nova_client, node_list):
    """
        Called directly from the web interface. Destroys nodes in provided list

        Args:
            nova_client - instance of Openstack Nova client object
            node_list - list of nodes to destroy

        Returns:
            None
    """
    destroy_network(nova_client, node_list)

# Test functions

def test_launch(username, password, img, flav, netname, util_ip, size, da_size):
    nova_client = create_novaclient(username,password)
    
    config = {'image': img,
	      'flavor': flav,
	      'netname': netname,
	      'util_ip': util_ip,
	      'size': size,
              'da_size': da_size}

    global num_nodes
    num_nodes = config['size']
                                    
    util_list = create_utilserv(nova_client, config)
    da_list = create_dirauth(nova_client, config)
    exit_list = create_exitnode(nova_client, config)
    relay_list = create_relaynode(nova_client, config)
    client_list = create_clientnode(nova_client, config)
    nodes = {'client': client_list,
             'relay': relay_list,
             'exit': exit_list,
             'da': da_list,
             'util': util_list}

    return nodes

def test_dismantle(username, password, node_list):
    nova_client = create_novaclient(username, password)
    destroy_network(nova_client, node_list)

# Main

if __name__ == '__main__':
    nova_client = create_novaclient(None,None)
    while(True):
        print("\nOpenstack SDK Backend - Main Menu")
        print("1. Reporting Options")
        print("2. Instance Options")
        print("3. Toggle debug")
        print("4. Exit")
        try:
            case = int(input("Enter choice: "))
        except:
            case = 6
        if case == 1:
            list_hub(nova_client)
        elif case == 2:
            instance_hub(nova_client)
        elif case == 3:
            toggle_debug()
        elif case == 4:
            print("Goodbye")
            exit()
        else:
            print("\nInvalid option")
