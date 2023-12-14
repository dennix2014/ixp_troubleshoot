import ast
import json
import os
import random
import string
from netmiko import ConnectHandler
from ixp_troubleshoot.hosts import rs_ipv4, rs_ipv6, ssh_params
from ixp_troubleshoot.settings import BASE_DIR
from pprint import pprint as pp
import ipaddress
import socket
import ast

ALPHANUMERIC_STRING = string.ascii_lowercase + string.digits
STRING_LENGTH = 4

from dotenv import load_dotenv
from pathlib import Path
import re

dotenv_path = Path('/home/noc-admin/.cred.env')
load_dotenv(dotenv_path=dotenv_path)


user = os.getenv('lab_user')
passw = os.getenv('lab_pass')
ssh_user = 'tshoot'
ssh_pass = "tshoot"
ssh_port = 22
key_file = '/home/noc-admin/.ssh/id_rsa.pub'
session_log = '/home/noc-admin/netmiko.log'
primary_rs = '192.168.100.100'


def is_engineer(user):
    return user.groups.filter(name='ENGINEERS').exists() or \
        user.is_superuser


def is_accountant(user):
    return user.groups.filter(name='ACCOUNTANTS').exists() or \
        user.is_superuser


def is_noc(user):
    return user.groups.filter(name='NOC').exists() or \
        user.is_superuser


def generate_random_string(chars=ALPHANUMERIC_STRING, length=STRING_LENGTH):
    return "".join(random.choice(chars) for _ in range(length))




def perform_l1_l2_test(**kwargs):
    ssh_params  = {
        'device_type': kwargs.get('netmiko_device_type'),
        'host': kwargs.get('switch'),
        'username': user,
        'password': passw,
        'port': kwargs.get('ssh_port'),
        'fast_cli': True
    }

    ports = kwargs.get('ports')
    channelgroup = kwargs.get('channelgroup')

    net_connect = ConnectHandler(**ssh_params)

    l2_status = ''
    out = {}

    for port in ports:
        if_name = port.split('_')[0]
        if_description = port.split('_')[1]
        command = f'sh int {if_name} | inc {if_description}|Description|seconds|Port'
        output = net_connect.send_command(command)
        if 'down' in output and not channelgroup:
            status = 'FAILED'
            l2_status = 1
        else:
            status = 'PASSED'
            l2_status = 0

        out[if_description] = [output, status]
    if channelgroup:
        command = f'sh int Port-Channel{channelgroup} | inc Port-Channel{channelgroup}|Description|seconds|Ethernet|Active'
        output = net_connect.send_command(command)
        if 'down' in output:
            status = 'FAILED'
            l2_status = 1
        else:
            status = 'PASSED'
            l2_status = 0
        out[f'Port-Channel{channelgroup}'] = [output, status]

    net_connect.disconnect()
    out['l2_status'] = l2_status
    return out

def perform_basic_l3_test(server, ip_address):
    ssh_params['host'] = server

    new_con = ConnectHandler(**ssh_params)
    output = new_con.send_command(f'ping {ip_address} ; exit_code=$?')
    exit_code = new_con.send_command('echo $exit_code')
    return [output, exit_code]

def connect_to_route_server(server, command):
    ssh_params['host'] = server
    net_connect = ConnectHandler(**ssh_params)
    output = net_connect.send_command(command, delay_factor=2)
    output = ast.literal_eval(output)
    net_connect.disconnect()
    if 'shprodetail' in command:
        if output:
            if output.get('bgp_state') != 'Established':
                bgp_status = 1
            else:
                bgp_status = 0
        else:
            output = {
                'bgp_state': 'BGP Peer not Found',
                'since': 'forever',
                'imported': 0,
                'exported': 0
            }
            bgp_status = 1

        return [output, bgp_status]
    elif 'shpref' in command:
        table_header = ['prefix', 'origin', 'path']
        table_id = 'received'
        ip_col = table_header.index('prefix') + 1

        pp(output)
        
        return [output, table_header, table_id, ip_col]

def get_peers(ip_protocol):
    rs = list({v[0] for v in ip_protocol.values()})
    command = 'getpeers'
    peers = {}
    for s in rs:
        ssh_params['host'] = s
        net_connect = ConnectHandler(**ssh_params)
        output = net_connect.send_command(command, delay_factor=2)
        output = ast.literal_eval(output)
        output = {item.get('neighbor_ip'):item.get('peer') for item in output}
        peers.update(output)

    return peers


def get_log(**kwargs):
    ssh_params  = {
        'device_type': kwargs.get('netmiko_device_type'),
        'host': kwargs.get('switch'),
        'username': user,
        'password': passw,
        'port': kwargs.get('ssh_port'),
        'fast_cli': False
    }

    ports = kwargs.get('ports')
    channelgroup = kwargs.get('channelgroup')

    net_connect = ConnectHandler(**ssh_params)
    out = []
    
    out_intf = {}
    for port in ports:
        if_name = port.split('_')[0]
        if_description = port.split('_')[1]
        command = f'sh logging | inc {if_name}'
        output = net_connect.send_command(command)
        if output:
            out_intf['log'] = output
        else:
            out_intf['log'] = 'Nothing to show'

        out_intf['interface'] = if_description
        
        out.append(out_intf)
        out_intf = {}
    if channelgroup:
        command = f'sh logging | inc Port-Channel{channelgroup}'
        output = net_connect.send_command(command)
        if output:
            out_intf['log'] = output
        else:
            out_intf['log'] = 'Nothing to show'

        out_intf['interface'] = f'Port-Channel{channelgroup}'
        out.append(out_intf)

    net_connect.disconnect()

    return out


def resolve_domain(domain_name):
    try:
        ip_address = socket.gethostbyname(domain_name)
        return ip_address
    except socket.error as e:
        ip_address = 0
        return ip_address

def is_valid_ipv4(ip_address):
    try:
        # Attempt to create an IPv4 address object
        ip_obj = ipaddress.IPv4Address(ip_address)
        return True
    except ipaddress.AddressValueError:
        # Raised when the input is not a valid IPv4 address
        return False


def bytes_to_gb(bytes_size):
    gb_size = bytes_size / (1000 ** 3)  # 1 GB = 1000^3 bytes
    return int(gb_size)

def connect_to_switch(**kwargs):
    ssh_params  = {
        'device_type': 'arista_eos',
        'host': kwargs.get('switch'),
        'username': user,
        'password': passw,
        'port': 22,
        'fast_cli': True
    }

    port = kwargs.get('port')
 

    net_connect = ConnectHandler(**ssh_params)
    response = net_connect.send_command(f'sh int {port} status | json')

    net_connect.disconnect()
    response = json.loads(response)
    parsed_response = {}

    
    details = response['interfaceStatuses'].get(port)
    bandwidth = f'{bytes_to_gb(details.get("bandwidth"))}GB'
    interface_type = details.get('interfaceType')
    description = details.get('description')
    link_status = details.get('linkStatus')

    parsed_response['interface'] = port
    parsed_response['bandwidth'] = bandwidth
    parsed_response['interface_type'] = interface_type
    parsed_response['description'] = description
    parsed_response['link_status'] = link_status
  
    return parsed_response

def ping_peer(peer_ip):

    ssh_params  = {
        'device_type': 'linux',
        'host': primary_rs,
        'username': ssh_user,
        'password': ssh_pass,
        'port': ssh_port,
        'session_log': session_log,
        'fast_cli': True
    }

    new_con = ConnectHandler(**ssh_params)
    output = new_con.send_command(f'ping {peer_ip} ; exit_code=$?')
    exit_code = new_con.send_command('echo $exit_code')
    return [output, exit_code]


def check_bgp_status(peer):
    ssh_params  = {
        'device_type': 'linux',
        'host': primary_rs,
        'username': ssh_user,
        'password': ssh_pass,
        'port': ssh_port,
        'session_log': session_log,
        'fast_cli': True
    }

    
    net_connect = ConnectHandler(**ssh_params)
    output = net_connect.send_command(f'shprodetail {peer}', delay_factor=2)
    output = ast.literal_eval(output)
    net_connect.disconnect()

 
    if output:
        if output.get('bgp_state') != 'Established':
            bgp_status = 1
        else:
            bgp_status = 0
    else:
        output = {
            'bgp_state': 'BGP Peer not Found',
            'since': 'forever',
            'imported': 0,
            'exported': 0
        }
        bgp_status = 1

    return [output, bgp_status]

def check_prefix(ip_prefix):
    ssh_params  = {
        'device_type': 'linux',
        'host': primary_rs,
        'username': ssh_user,
        'password': ssh_pass,
        'port': ssh_port,
        'session_log': session_log,
        'fast_cli': True
    }

    new_con = ConnectHandler(**ssh_params)
    net_connect = ConnectHandler(**ssh_params)
    output = net_connect.send_command(f'please show route for  {ip_prefix} all', delay_factor=2)
    net_connect.disconnect()

    # Define regular expressions to extract relevant information
    ip_cidr_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+/\d+)')
    as_path_pattern = re.compile(r'BGP.as_path: (\d+)')
    next_hop_pattern = re.compile(r'BGP.next_hop: (\d+\.\d+\.\d+\.\d+)')
    med_pattern = re.compile(r'BGP.med: (\d+)')
    local_pref_pattern = re.compile(r'BGP.local_pref: (\d+)')
    community_pattern = re.compile(r'BGP.community: \((\d+),(\d+)\)')
    peer_name_pattern = re.compile(r'\[([^\]]+?)\s+\d{2}:\d{2}:\d{2}\]')
    #peer_name_pattern = re.compile(r'\[([^\]]+?)\s+\d{4}-\d{2}-\d{2}\]')

    # Initialize an empty dictionary to store the extracted information
    output_dict = {}

    # Find matches in the input string and populate the dictionary
    ip_cidr_match = ip_cidr_pattern.search(output)
    if ip_cidr_match:
        output_dict['ip_cidr'] = ip_cidr_match.group(1)

    as_path_match = as_path_pattern.search(output)
    if as_path_match:
        output_dict['as_path'] = int(as_path_match.group(1))

    next_hop_match = next_hop_pattern.search(output)
    if next_hop_match:
        output_dict['next_hop'] = next_hop_match.group(1)

    med_match = med_pattern.search(output)
    if med_match:
        output_dict['med'] = int(med_match.group(1))

    local_pref_match = local_pref_pattern.search(output)
    if local_pref_match:
        output_dict['local_pref'] = int(local_pref_match.group(1))

    peer_name_match = peer_name_pattern.search(output)
    if peer_name_match:
        output_dict['peer_name'] = peer_name_match.group(1)

    community_match = community_pattern.search(output)
    if community_match:
        output_dict['community'] = (int(community_match.group(1)), int(community_match.group(2)))

    return output_dict




