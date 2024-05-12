#!/usr/bin/python3
# helper.py

import os, socket, requests, json
from cloudflare_dns import find_record, add_record, delete_record

get_timeout_s = int(os.environ["GET_TIMEOUT_S"])
up_threshold_ticks = int(os.environ["UP_THRESHOLD_TICKS"])
down_threshold_ticks = int(os.environ["DOWN_THRESHOLD_TICKS"])

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
    return string1==string2 or string1 == "random_string"

def monitor(subdomain, FQDN, record_list, uptime, downtime, recorded, zone_id):
    for i in range(len(record_list)):
        try:
            dns_cache[FQDN] = record_list[i]["ip_address"]
            response = requests.get(f"http://{FQDN}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')}", timeout=get_timeout)
            status_code_range = record_list[i].get("status_code_range", [[200,299]])
            if not within_range(status_code_range, int(response.status_code)) or not string_match(record_list[i].get("match_string", "random_string"), response.text):
                raise requests.RequestException()
            
            # node is up
            print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} UP")
            uptime[i] += 1
            downtime[i] = 0
            if not recorded[i] and uptime[i] >= up_threshold_ticks:
                # add record to cloudflare dns zone
                success = add_record(record_list[i]['ip_address'], subdomain, zone_id)
                if success:
                    print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} ADD SUCCESSFUL")
                    recorded[i] = True
                else:
                    print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} ADD FAILED")
                uptime[i] == 0
        except:
            # node is not right
            print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} NO ANSWER")
            uptime[i] = 0
            downtime[i] += 1
            if downtime[i] == down_threshold_ticks and recorded[i]:
                # node is down
                record_id, found = find_record(record_list[i]['ip_address'], FQDN, zone_id)
                if found:
                    # delete record from cloudflare dns zone
                    success = delete_record(record_id, zone_id)
                    if success:
                        recorded[i] = False
                        print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} DELETE SUCCESSFUL")
                    else:
                        print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} DELETE FAILED")
                else:
                    print(f"{record_list[i]['ip_address']}:{record_list[i].get('port', 80)}{record_list[i].get('path', '/')} not found on cloudflare")
                downtime[i] = 0