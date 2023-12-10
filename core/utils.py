import ast
import json
import os
import random
import string
from netmiko import ConnectHandler
from ixp_troubleshoot.hosts import rs_ipv4, rs_ipv6, ssh_params
from ixp_troubleshoot.settings import BASE_DIR
from pprint import pprint as pp

ALPHANUMERIC_STRING = string.ascii_lowercase + string.digits
STRING_LENGTH = 4

from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/home/noc-admin/.cred.env')
load_dotenv(dotenv_path=dotenv_path)

user = os.getenv('RADUSR')
passw = os.getenv('RADPASS')


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

        pp(output)
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













