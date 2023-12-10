from django.http import JsonResponse, response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cust, Vlaninterface, Switch, MemberDetails, SwitchMain
from ixp_troubleshoot.settings import BASE_DIR
from ixp_troubleshoot.hosts import switches, rs_ipv4, rs_ipv6, rs
import json
from zipfile import ZipFile, ZIP_DEFLATED
import pathlib
from core.utils import perform_l1_l2_test, perform_basic_l3_test, connect_to_route_server, get_peers, get_log


error_msg = 'Correct errors indicated and try again'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def list_switches(request):
    switches = SwitchMain.objects.all()
    context = {'switches' : switches}
    return render(request, 'list_switches.html', context)


@login_required
def list_peers(request):
    peers = MemberDetails.objects.all()
    context = {'peers': peers}
    return render(request, 'list_peers.html', context)

@login_required
def update_peers(request):
    peers = get_peers(rs_ipv4)
    peers_v6 = get_peers(rs_ipv6)
    vlan_interfaces = Vlaninterface.objects.using('ixpm').all()

    MemberDetails.truncate()

    for item in vlan_interfaces:

        peer = MemberDetails()
        ipv4addr = item.ipv4addressid.address
        name = peers.get(ipv4addr)
        if name:
            peer.name = name
        else:
            peer.name = item.virtualinterfaceid.custid.name
        
        peer.ipv4addr = ipv4addr
        ipv6addr = item.ipv6addressid.address
        peer.ipv6addr = ipv6addr

        if peers_v6.get(ipv6addr):
            ipv6_enabled = True 
        else:
            ipv6_enabled = False 
        
        peer.ipv6_enabled = ipv6_enabled

        ports = [f'{entry.switchportid.ifname}_{entry.switchportid.name}' \
                for entry in item.virtualinterfaceid.physicalinterface_set.all()]

        speed = [entry.speed \
                for entry in item.virtualinterfaceid.physicalinterface_set.all()]

        peer.connected_ports = ports
        peer.speed = speed
        switchid = item.virtualinterfaceid.physicalinterface_set.first().switchportid.switchid.id
        switchid = get_object_or_404(SwitchMain, pk=switchid)
        peer.switchid = switchid
        peer.switch_ip = switchid.ipv4addr
        peer.peering_policy = item.virtualinterfaceid.custid.peeringpolicy
        peer.channelgroup = item.virtualinterfaceid.channelgroup
        peer.asn = item.virtualinterfaceid.custid.autsys
        peer.save()

    return redirect('list_peers')


@login_required
def update_switches(request):
    switches  = Switch.objects.using('ixpm').all()

    with open(f'{BASE_DIR}/core/switch_models.json') as s:
        switch_models = json.load(s)

    SwitchMain.truncate()
    
    for item in switches:
        switch = SwitchMain()

        switch.name = item.name
        vendor = item.vendorid.name
        if vendor:
            switch.vendor = vendor
        else:
            switch.vendor = 'cisco_ios'
        switch.ipv4addr = item.hostname
        switch.infrastructure = item.infrastructure.name
        switch.pop = item.cabinetid.locationid.name
        switch.switchid = item.id
        switch.netmiko_device_type = switch_models.get(vendor)

        switch.save()


    peers = get_peers(rs_ipv4)
    peers_v6 = get_peers(rs_ipv6)
    vlan_interfaces = Vlaninterface.objects.using('ixpm').all()

    MemberDetails.truncate()

    for item in vlan_interfaces:
        print(item.virtualinterfaceid.custid.autsys)

        peer = MemberDetails()
        ipv4addr = item.ipv4addressid.address
        name = peers.get(ipv4addr)
        print(name)
        if name:
            peer.name = name
        else:
            peer.name = item.virtualinterfaceid.custid.name
        
        peer.ipv4addr = ipv4addr
        ipv6addr = item.ipv6addressid.address
        peer.ipv6addr = ipv6addr

        if peers_v6.get(ipv6addr):
            ipv6_enabled = True 
        else:
            ipv6_enabled = False 
        
        peer.ipv6_enabled = ipv6_enabled

        ports = [f'{entry.switchportid.ifname}_{entry.switchportid.name}' \
                for entry in item.virtualinterfaceid.physicalinterface_set.all()]

        speed = [entry.speed \
                for entry in item.virtualinterfaceid.physicalinterface_set.all()]

        peer.connected_ports = ports
        peer.speed = speed
        print(speed)
        print('=========================')
        switchid = item.virtualinterfaceid.physicalinterface_set.first().switchportid.switchid.id
        switchid = get_object_or_404(SwitchMain, pk=switchid)
        peer.switchid = switchid
        peer.switch_ip = switchid.ipv4addr
        peer.peering_policy = item.virtualinterfaceid.custid.peeringpolicy
        peer.channelgroup = item.virtualinterfaceid.channelgroup
        peer.asn = item.virtualinterfaceid.custid.autsys
        peer.save()


    ### Creating or updating the json file that will be used by the subscription monitor script.

    peers = MemberDetails.objects.all()
    switches = SwitchMain.objects.all()
    switchez = []
    for switch in switches:
        swi = {}
        swi_ip = switch.ipv4addr
        swi_name = switch.name
        vendor = switch.vendor
        pop = switch.get_pop_display()
        swi['ip_add'] = swi_ip
        swi['port_params'] = swi_name
        swi['pop'] = pop
        swi['vendor'] = vendor
        switchez.append(swi)

        peers_on_switch = peers.filter(switch_ip=swi_ip)


        peerz = []
        for peer in peers_on_switch:
            det = {}
            if peer.channelgroup:
                det['port'] = f'Po{peer.channelgroup}'
            else:
                port = f'{(peer.interface_description)[0]}'
                if 'Arista' in vendor:
                    port = port.replace('Ethernet', 'Et')

                det['port'] = port
            
            det['port_name'] = peer.name
            det['subscription_GB'] = peer.total_speed
            raw_speed = peer.raw_speed
            det['subscription'] = raw_speed
            det['threshold'] = int(raw_speed) * 0.8

            peerz.append(det)

        with open(f'./peering_params/{swi_name}.json', 'w') as params:
            json.dump(peerz, params, indent=2)

    with open('./peering_params/switches.json', 'w') as swi_params:
            json.dump(switchez, swi_params, indent=2)

    zipped_file = './peering_params.zip'
    dir_to_be_zipped = './peering_params'

    folder = pathlib.Path(dir_to_be_zipped)

    with ZipFile(zipped_file, "w", ZIP_DEFLATED) as zip_obj:
        for file in folder.iterdir():
            zip_obj.write(file)

    return redirect('list_switches')


@login_required
def l1_l2_test(request, pk):
    peer = get_object_or_404(MemberDetails, pk=pk)
    peer_id = pk
    name = peer.name
    asn = peer.asn
    pop = peer.switchid.get_pop_display()
    infrastructure = peer.switchid.infrastructure
    ports = peer.connected_ports
    switch = peer.switchid.ipv4addr
    netmiko_device_type = switches.get(switch)
    ssh_port = switches.get(switch)
    channelgroup = peer.channelgroup
    peering_policy = peer.peering_policy
    ipv6_enabled = peer.ipv6_enabled

    if netmiko_device_type:


        results = perform_l1_l2_test(
                    switch=switch,
                    ports=ports,
                    netmiko_device_type=netmiko_device_type[0],
                    channelgroup=channelgroup,
                    ssh_port=ssh_port[1]
                )

        l2_status = results.get('l2_status')
        del results['l2_status']
    
    else:
        ports = [port.split('_')[1] for port in ports]
        ports = ' '.join(ports)
        results = {
            f'{ports}': ['switch not supported', 'FAILED']
            
        }

        l2_status = 1

    context = {
        'results': results, 
        'name': name, 
        'asn':asn, 
        'pop':pop, 
        'peer_id': peer_id,
        'infrastructure': infrastructure,
        'l2_status': l2_status,
        'pp': peering_policy,
        'ipv6_enabled': ipv6_enabled
        }

    return render(request, 'l1_l2.html', context)


@login_required
def l3_basic_test(request, pk):
    peer = get_object_or_404(MemberDetails, pk=pk)
    ipv4addr = peer.ipv4addr
    ipv6addr = peer.ipv6addr
    pop = peer.switchid.get_pop_display()
    infrastructure = peer.switchid.infrastructure
    ip_protocol = request.GET['ipProtocol']
    if ip_protocol == 'ipv4':
        ip_address = ipv4addr
    else:
        ip_address = ipv6addr

    server = (rs.get(ip_protocol)).get(infrastructure)
    if server:
        server = server[0]
        output = perform_basic_l3_test(
            server,
            ip_address
                )

        response = {
            'output': output[0], 
            'l3_status': output[1],
            'pop':pop, 
            'ip_protocol': ip_protocol
        }

        return JsonResponse(response)
    else:
        response = {
            'output': f'No Route server at {pop}',
            'l3_status': 1,
            'pop': pop,
            'ip_protocol': ip_protocol

        }

        return JsonResponse(response)

@login_required
def bgp_neighbor_received(request):
    if request.method == 'GET' and is_ajax(request):
        peer = request.GET['peerId']
        pop = (get_object_or_404(MemberDetails, pk=peer)).switchid.get_pop_display()
        infrastructure = request.GET['infrastructure']
        bgp_peer = request.GET['bgpPeer']
        ip_protocol = request.GET['ipProtocol']

        server = (rs.get(ip_protocol)).get(infrastructure)[0]
        command = 'shpref'

        

        if "HURRICANE" in bgp_peer:
            result = 'Route recieved too long'
            is_table = 0
            response = {
                'result':result,
            }
            return JsonResponse(response)
        else:       
            command_to_run = f'{command} {bgp_peer}'
            result = connect_to_route_server(server, command_to_run)
                
            response = {
                'result':result[0], 
                'table_header': result[1],
                'table_id': result[2],
                'ip_col': result[3],
                'bgp_peer': bgp_peer,
                'infrastructure': infrastructure,
                'pop': pop,
                'ip_protocol':ip_protocol
            }
            return JsonResponse(response)


@login_required
def bgp_status(request):
    if request.method == 'GET' and is_ajax(request):

        infrastructure = request.GET['infrastructure']
        bgp_peer = request.GET['bgpPeer']
        ip_protocol = request.GET['ipProtocol']

        server = (rs.get(ip_protocol)).get(infrastructure)[0]
        command = 'shprodetail'

        command_to_run = f'{command} {bgp_peer}'
        result = connect_to_route_server(server, command_to_run)

        response = {
            'result':result[0],
            'bgp_status': result[1]
        }
        return JsonResponse(response)


@login_required
def fetch_logs(request, pk):
    peer = get_object_or_404(MemberDetails, pk=pk)
    switch = peer.switchid.ipv4addr
    netmiko_device_type = switches.get(switch)
    ssh_port = switches.get(switch)
    channelgroup = peer.channelgroup
    ports = peer.connected_ports
    table_header = ['interface', 'log']
    if netmiko_device_type:

        results = get_log(
                    switch=switch,
                    ports=ports,
                    netmiko_device_type=netmiko_device_type[0],
                    channelgroup=channelgroup,
                    ssh_port=ssh_port[1]
                )
    else:
        
        ports = [port.split('_')[1] for port in ports]
        ports = ' '.join(ports)
        results = [
            {
                'log': 'switch not supported',
                'interface': f'{ports}'
            }
        ]

    response = {
        'results': results, 
        'table_header': table_header
        }

    return JsonResponse(response)


