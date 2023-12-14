from django.http import JsonResponse, response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Switch, MemberDetails
from ixp_troubleshoot.settings import BASE_DIR
from ixp_troubleshoot.hosts import switches, rs_ipv4, rs_ipv6, rs
import json
import os
from.forms import L3ReachabilityForm, SwitchForm, MemberDetailsForm
from zipfile import ZipFile, ZIP_DEFLATED
import pathlib
from core.utils import (resolve_domain,
                        is_valid_ipv4,
                        connect_to_switch,
                        ping_peer,
                        check_bgp_status,
                        check_prefix)


error_msg = 'Correct errors indicated and try again'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def home(request):
    return redirect('account_login')

@login_required
def list_switches(request):
    switches = Switch.objects.all()
    context = {'switches' : switches}
    return render(request, 'list_switches.html', context)


@login_required
def list_peers(request):
    peers = MemberDetails.objects.all()
    context = {'peers': peers}
    return render(request, 'list_peers.html', context)


                
@login_required
def l3_reachability(request):
    if request.method == 'POST':
        form = L3ReachabilityForm(request.POST)
        if form.is_valid():
            resolved_ip = None
            member = form.cleaned_data['member']
            ip_address = form.cleaned_data['ip_address_or_hostname']
            raw_ip_address = ip_address
            check_if_ipv4 = is_valid_ipv4(ip_address)
            check_if_hostname = resolve_domain(ip_address)

            if check_if_ipv4:
                is_received_entry_ipv4 = True
            elif check_if_hostname:
                is_received_entry_ipv4 = False

            if check_if_ipv4 or (resolved_ip := check_if_hostname):
                member_details = MemberDetails.objects.get(name=member)
                peer_name = member_details.name
                switch_ip = member_details.switch.ipv4addr

                port = (member_details.connected_ports)
                peer_ip = member_details.ipv4addr
                peering_policy = member_details.peering_policy
                

                interface_status_check = connect_to_switch(port=port, switch=switch_ip)
                if interface_status_check.get('link_status') == 'connected':
                    port_status = f'Interface for {peer_name} is connected!'
                    peer_ping_check = ping_peer(peer_ip)
                    
                    if not int(peer_ping_check[1]):
                        peer_ping_status = f"{peer_name}'s peer ip - {peer_ip} is reachable!"
                        if peering_policy == 'open':
                            peer_bgp_check = check_bgp_status(peer_name)

                            if not int(peer_bgp_check[1]):
                                peer_bgp_check_status = f"{peer_name}'s BGP session is Established!"
                                check_ip_prefix = check_prefix(resolved_ip or ip_address)
                                
                                if check_ip_prefix:
                                    check_ip_prefix_status = f"{raw_ip_address} is available at the IX!"
                                    other_peer_ip = check_ip_prefix.get('next_hop')
                                    other_peer_ping_check = ping_peer(other_peer_ip)
                                    print(check_ip_prefix)

                                    if not int(other_peer_ping_check[1]):
                                        other_peer_name = check_ip_prefix.get('peer_name')
                                        other_peer_ip = check_ip_prefix.get('next_hop')
                                        other_peer_ping_check_status = f'{other_peer_name} peer ip - {other_peer_ip} is reachable!'
                                        service_ping_check = ping_peer(resolved_ip or ip_address)

                                        if not int(service_ping_check[1]):
                                            service_ping_check_status = f'{raw_ip_address} is reachable!'
                        
                                            return render(
                                                        request, 
                                                        'report.html', {
                                                            'member': member, 
                                                            'ip_address': raw_ip_address,
                                                            'interface_status': interface_status_check,
                                                            'peer_ping_check': peer_ping_check,
                                                            'peer_bgp_check': peer_bgp_check,
                                                            'other_peer_ping_check': other_peer_ping_check[0],
                                                            'service_ping_check': service_ping_check[0],
                                                            'port_status': port_status,
                                                            'service_ping_check_status': service_ping_check_status,
                                                            'other_peer_ping_check_status': other_peer_ping_check_status,
                                                            'check_ip_prefix_status': check_ip_prefix_status,
                                                            'peer_bgp_check_status': peer_bgp_check_status,
                                                            'peer_ping_status': peer_ping_status

                                                        })

                                        else:
                                            service_ping_check_status = f'{raw_ip_address} is not reachable!'
                                            return render(
                                            request, 
                                            'report.html', {
                                                'member': member, 
                                                'ip_address': raw_ip_address,
                                                'interface_status': interface_status_check,
                                                'peer_ping_check': peer_ping_check,
                                                'peer_bgp_check': peer_bgp_check,
                                                'other_peer_ping_check': other_peer_ping_check[0],
                                                'service_ping_check': service_ping_check[0],
                                                'service_ping_check_status': service_ping_check_status,
                                                'other_peer_ping_check_status': other_peer_ping_check_status,
                                                'check_ip_prefix_status': check_ip_prefix_status,
                                                'peer_bgp_check_status': peer_bgp_check_status,
                                                'port_status': port_status,
                                                'peer_ping_status': peer_ping_status
                                            })

                                    else:
                                        other_peer_ping_check_status = f"{other_peer_name}'s peer ip - {other_peer_ip} is not reachable!"
                                        return render(
                                            request, 
                                            'report.html', {
                                                'member': member, 
                                                'ip_address': raw_ip_address,
                                                'interface_status': interface_status_check,
                                                'peer_ping_check': peer_ping_check,
                                                'peer_bgp_check': peer_bgp_check,
                                                'other_peer_ping_check': other_peer_ping_check[0],
                                                'other_peer_ping_check_status': other_peer_ping_check_status,
                                                'check_ip_prefix_status': check_ip_prefix_status,
                                                'peer_bgp_check_status': peer_bgp_check_status,
                                                'port_status': port_status,
                                                'peer_ping_status': peer_ping_status
                                            })

                                else:
                                    check_ip_prefix_status = f'{raw_ip_address} not available at the IX'
                                    return render(
                                        request, 
                                        'report.html', {
                                        'member': member, 
                                        'ip_address': raw_ip_address,
                                        'interface_status': interface_status_check,
                                        'peer_ping_check': peer_ping_check,
                                        'peer_bgp_check': peer_bgp_check,
                                        'check_ip_prefix_status': check_ip_prefix_status,
                                        'check_ip_prefix': f'{raw_ip_address} not available at the IX',
                                        'peer_bgp_check_status': peer_bgp_check_status,
                                        'port_status': port_status,
                                        'peer_ping_status': peer_ping_status
                                    })
                                        

                            else:
                                peer_bgp_check_status = f"{peer_name}'s BGP session is not Established!"
                                return render(
                                request, 
                                'report.html', {
                                    'member': member, 
                                    'ip_address': raw_ip_address,
                                    'interface_status': interface_status_check,
                                    'peer_ping_check': peer_ping_check,
                                    'peer_bgp_check': peer_bgp_check,
                                    'peer_bgp_check_status': peer_bgp_check_status,
                                    'port_status': port_status,
                                    'peer_ping_status': peer_ping_status


                                }) 
                        

                        else:
                            return render(
                                request, 
                                'report.html', {
                                    'member': member, 
                                    'ip_address': raw_ip_address,
                                    'interface_status': interface_status_check,
                                    'peer_ping_check': peer_ping_check,
                                    'peering_policy_message': f"{member}'s peering policy is not open, therefore there is no bgp peer on the route server",
                                    'port_status': port_status,
                                    'peer_ping_status': peer_ping_status
                                })  
                            
                    else:
                        peer_ping_status = f"{peer_name}'s peer ip - {peer_ip} is not reachable!"
                        return render(
                                request, 
                                'report.html', {
                                    'member': member, 
                                    'ip_address': raw_ip_address,
                                    'interface_status': interface_status_check,
                                    'peer_ping_check': peer_ping_check,
                                    'port_status': port_status,
                                    'peer_ping_status': peer_ping_status
                                })                
                
                else:
                    port_status = f'Interface for {peer_name} is not connected!'
                    return render(
                                request, 
                                'report.html', {
                                    'member': member, 
                                    'ip_address': raw_ip_address,
                                    'interface_status': interface_status_check,
                                    'port_status': port_status
                                })

            else:
                form.add_error('ip_address_or_hostname', 'Please enter a valid IP address or domain name')
            
    else:
        form = L3ReachabilityForm()

    return render(request, 'l3_reachability.html', {'form': form})

@login_required
def add_or_edit_switch(request, pk=None):
   
    switch_obj = get_object_or_404(Switch, pk=pk) if pk else None
    form = SwitchForm(request.POST, request.FILES, instance=switch_obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('list_peers')
        else:
            messages.error(request, error_msg)
            return render(request, 'add_or_edit_switch.html', {'form': form})
    elif request.method == 'GET':
        form = SwitchForm(instance=switch_obj)
        context = {
           'form': form, 
           'switch_obj': switch_obj,
           }

    return render(request, 'add_or_edit_switch.html', context)

@login_required
def add_or_edit_member(request, pk=None):
   
    member_obj = get_object_or_404(MemberDetails, pk=pk) if pk else None
    form = MemberDetailsForm(request.POST, request.FILES, instance=member_obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('list_peers')
        else:
            messages.error(request, error_msg)
            return render(request, 'add_or_edit_member.html', {'form': form})
    elif request.method == 'GET':
        form = MemberDetailsForm(instance=member_obj)
        context = {
           'form': form, 
           'member_obj': member_obj,
           }

    return render(request, 'add_or_edit_member.html', context)