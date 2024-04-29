#!/usr/bin/python3
# helper.py

import os, socket, requests, json
from cloudflare_dns import find_record, add_record, delete_record

get_timeout = int(os.environ["GET_TIMEOUT"])
up_threshold = int(os.environ["UP_THRESHOLD"])
down_threshold = int(os.environ["DOWN_THRESHOLD"])

dns_cache = {}

# override the default dns resolver that requests.get calls under the hood
prv_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args):
    if args[0] in dns_cache:
        return prv_getaddrinfo(dns_cache[args[0]], *args[1:])
    else:
        return prv_getaddrinfo(*args)
socket.getaddrinfo = new_getaddrinfo

def get_hosts_from_env():
    return json.loads(os.environ["HOSTS"])

def within_range(status_code_range, status_code):
    for code_or_range in status_code_range:
        if isinstance(code_or_range, int):
            if status_code == code_or_range:
                return True
        elif isinstance(code_or_range, list) and len(code_or_range) == 2:
            start, end = code_or_range
            if start <= status_code and status_code <= end:
                return True
        else:
            raise TypeError("A status code range is in a wrong format")
    return False

def string_match(string1, string2):
    return string1==string2

def monitor(subdomain, FQDN, ip_addr_list, uptime, downtime, recorded, zone_id):
    for i in range(len(ip_addr_list)):
        try:
            dns_cache[FQDN] = ip_addr_list[i]["ip_address"]
            # TODO: add path in the URL
            response = requests.get(f"http://{FQDN}:{ip_addr_list[i]['port']}", timeout=get_timeout)
            # TODO: make default range an environment variable
            status_code_range = ip_addr_list[i]["status_code_range"] if ip_addr_list[i].get("status_code_range") else [[200, 299]]
            if not within_range(status_code_range, int(response.status_code)) or not string_match(ip_addr_list[i]["match_string"], response.text):
                raise requests.RequestException()
            print(f"{FQDN}: {ip_addr_list[i]['ip_address']} with port {ip_addr_list[i]['port']} and path {ip_addr_list[i]['path']} UP")
            uptime[i] += 1
            downtime[i] = 0
            if not recorded[i] and uptime[i] >= up_threshold:
                # add record to cloudflare dns zone
                success = add_record(ip_addr_list[i]["ip_address"], subdomain, zone_id)
                if success:
                    print(f"{FQDN}: {ip_addr_list[i]['ip_address']} ADD SUCCESSFUL")
                    recorded[i] = True
                else:
                    print(f"{FQDN}: {ip_addr_list[i]['ip_address']} ADD FAILED")
                uptime[i] == 0
        except:
            # failed connection (node is potentially down)
            print(f"{FQDN}: {ip_addr_list[i]['ip_address']} NO ANSWER")
            uptime[i] = 0
            downtime[i] += 1
            if downtime[i] == down_threshold and recorded[i]:
                # find dns id of the host
                record_id, found = find_record(ip_addr_list[i]["ip_address"], FQDN, zone_id)
                if found:
                    # delete record from cloudflare dns zone
                    success = delete_record(record_id, zone_id)
                    if success:
                        recorded[i] = False
                        print(f"{FQDN}: {ip_addr_list[i]['ip_address']} DELETE SUCCESSFUL")
                    else:
                        print(f"{FQDN}: ATTENTION! couldn't delete {ip_addr_list[i]['ip_address']} with its record id")
                else:
                    print(f"{FQDN}: record id of {ip_addr_list[i]['ip_address']} cannot be found on cloudflare")
                downtime[i] = 0
