#!/usr/bin/python3
# helper.py

import os, socket, requests, time
from cloudflare_dns import find_record, add_record, delete_record

get_timeout = int(os.environ["GET_TIMEOUT"])
up_num = int(os.environ["UP_NUM"])
down_num = int(os.environ["DOWN_NUM"])

dns_cache = {}
# override the default dns resolver that requests.get calls under the hood
prv_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args):
    if args[0] in dns_cache:
        return prv_getaddrinfo(dns_cache[args[0]], *args[1:])
    else:
        return prv_getaddrinfo(*args)
socket.getaddrinfo = new_getaddrinfo

def parse_domains_env_var(env_var_value):
    domains = {}

    domain_parts = env_var_value.split(';')
    for domain_part in domain_parts:
        subdomain_parts = domain_part.split(':')
        domain_name = subdomain_parts[0]
        domains[domain_name] = {}
        subdomain_parts = subdomain_parts[1:]
        for subdomain_part in subdomain_parts:
            ip_parts = subdomain_part.split(',')
            subdomain_name = ip_parts[0]
            domains[domain_name][subdomain_name] = ip_parts[1:]
            
    return domains

def get_domains_from_env():
    env_var_value = os.getenv('DOMAINS', '')
    return parse_domains_env_var(env_var_value)

def monitor(subdomain, FQDN, ip_addr_list, uptime, downtime, recorded, zone_id):
    for i in range(len(ip_addr_list)):
        try:
            dns_cache[FQDN] = ip_addr_list[i]
            response = requests.get(f"http://{FQDN}:8080", timeout=get_timeout)
            print(f"{FQDN}: {ip_addr_list[i]} UP")
            uptime[i] += 1
            downtime[i] = 0
            if not recorded[i] and uptime[i] >= up_num:
                # add record to cloudflare dns zone
                success = add_record(ip_addr_list[i], subdomain, zone_id)
                if success:
                    print(f"{FQDN}: {ip_addr_list[i]} ADD SUCCESSFUL")
                    recorded[i] = True
                else:
                    print(f"{FQDN}: {ip_addr_list[i]} ADD FAILED")
                uptime[i] == 0
        except:
            # failed connection (node is potentially down)
            print(f"{FQDN}: {ip_addr_list[i]} NO ANSWER")
            uptime[i] = 0
            downtime[i] += 1
            if downtime[i] == down_num and recorded[i]:
                # find dns id of the host
                record_id, found = find_record(ip_addr_list[i], zone_id)
                if found:
                    # delete record from cloudflare dns zone
                    success = delete_record(record_id, zone_id)
                    if success:
                        recorded[i] = False
                        print(f"{FQDN}: {ip_addr_list[i]} DELETE SUCCESSFUL")
                    else:
                        print(f"{FQDN}: ATTENTION! couldn't delete {ip_addr_list[i]} with its record id")
                else:
                    print(f"{FQDN}: record id of {ip_addr_list[i]} cannot be found on cloudflare")
                downtime[i] = 0
