#!/usr/bin/python3
# main.py

import time, os, json, sys
from cloudflare_dns import find_record, find_zones_under_account
from helper import get_hosts_from_env, monitor

# reading environment variable
delay = int(os.environ["DELAY"])
domain_subdomain_ips = get_hosts_from_env() # dictionary of domain to ip_addrs
cloudflare_refresh_period_ticks = int(os.environ["CLOUDFLARE_REFRESH_PERIOD_TICKS"])

# dictionary of domain to zone_id
domain_dict = find_zones_under_account()

# check domain_subdomain_ips
# print(json.dumps(domain_subdomain_ips, indent=2))
print(domain_dict)

# initialization of variables
uptime = {}
downtime = {}
recorded = {}
for domain in domain_subdomain_ips["domains"]:
    domain_name = domain["domain_name"]
    subdomains = domain_subdomain_ips["domains"][domain_name]["subdomains"]
    for subdomain in subdomains:
        subdomain_name = subdomain["subdomain_name"]
        FQDN = subdomain_name + '.' + domain_name
        ip_addr_list = subdomain["ip_addresses"]
        uptime[FQDN] = [0] * len(ip_addr_list)
        downtime[FQDN] = [0] * len(ip_addr_list)
        recorded[FQDN] = [find_record(ip_addr_list[i], FQDN, domain_dict[domain_name])[1] for i in range(len(ip_addr_list))]

# infinite loop
count = 0
while True:
    time.sleep(delay)
    
    # periodically check the status of records on cloudflare to update recorded
    # will add the record back up if someone manually deletes it on cloudflare by accident
    count += 1
    if count == cloudflare_refresh_period_ticks:
        for domain in domain_subdomain_ips["domains"]:
            domain_name = domain["domain_name"]
            subdomains = domain_subdomain_ips["domains"][domain_name]["subdomains"]
            for subdomain in subdomains:
                subdomain_name = subdomain["subdomain_name"]
                FQDN = subdomain_name + '.' + domain_name
                ip_addr_list = subdomain["ip_addresses"]
                recorded[FQDN] = [find_record(ip_addr_list[i], FQDN, domain_dict[domain_name])[1] for i in range(len(ip_addr_list))]
        count = 0
        
    # actual work
    for domain in domain_subdomain_ips["domains"]:
        domain_name = domain["domain_name"]
        subdomains = domain_subdomain_ips["domains"][domain_name]["subdomains"]
        for subdomain in subdomains:
            subdomain_name = subdomain["subdomain_name"]
            FQDN = subdomain_name + '.' + domain_name
            ip_addr_list = subdomain["ip_addresses"]
            monitor(subdomain_name, FQDN, ip_addr_list, uptime[FQDN], downtime[FQDN], recorded[FQDN], domain_dict[domain_name])
