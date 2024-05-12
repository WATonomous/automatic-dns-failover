#!/usr/bin/python3
# main.py

import time, os, json, sys
from cloudflare_dns import find_record, find_zones_under_account
from helper import get_hosts_from_env, monitor

# reading environment variable
tick_duration_s = int(os.environ["TICK_DURATION_S"])
domain_subdomain_ips = get_hosts_from_env() # dictionary of domain to ip_addrs
cloudflare_refresh_period_ticks = int(os.environ["CLOUDFLARE_REFRESH_PERIOD_TICKS"])

# dictionary of domain to zone_id
domain_zone_id = find_zones_under_account()

print(domain_subdomain_ips)
print(domain_zone_id)

# this delay is needed because of the overlapping existence of a terminating container/pod and a new container/pod
time.sleep(30)

# initialization of variables
uptime = {}
downtime = {}
recorded = {}
for j, domain in enumerate(domain_subdomain_ips["domains"]):
    domain_name = domain["domain_name"]
    subdomains = domain_subdomain_ips["domains"][j]["subdomains"]
    for subdomain in subdomains:
        subdomain_name = subdomain["subdomain_name"]
        FQDN = subdomain_name + '.' + domain_name
        record_list = subdomain["records"]
        uptime[FQDN] = [0] * len(record_list)
        downtime[FQDN] = [0] * len(record_list)
        recorded[FQDN] = [find_record(record_list[i]["ip_address"], FQDN, domain_zone_id[domain_name])[1] for i in range(len(record_list))]
        print(f"{FQDN} status: {recorded[FQDN]}")

# infinite loop
count = 0
while True:
    time.sleep(tick_duration_s)
    
    # periodically check the status of records on cloudflare to update recorded
    # will add the record back up if someone manually deletes it on cloudflare by accident
    count += 1
    if count == cloudflare_refresh_period_ticks:
        for j, domain in enumerate(domain_subdomain_ips["domains"]):
            domain_name = domain["domain_name"]
            subdomains = domain_subdomain_ips["domains"][j]["subdomains"]
            for subdomain in subdomains:
                subdomain_name = subdomain["subdomain_name"]
                FQDN = subdomain_name + '.' + domain_name
                record_list = subdomain["records"]
                recorded[FQDN] = [find_record(record_list[i]["ip_address"], FQDN, domain_zone_id[domain_name])[1] for i in range(len(record_list))]
        count = 0
        
    # actual work
    for j, domain in enumerate(domain_subdomain_ips["domains"]):
        domain_name = domain["domain_name"]
        subdomains = domain_subdomain_ips["domains"][j]["subdomains"]
        for subdomain in subdomains:
            subdomain_name = subdomain["subdomain_name"]
            FQDN = subdomain_name + '.' + domain_name
            record_list = subdomain["records"]
            monitor(subdomain_name, FQDN, record_list, uptime[FQDN], downtime[FQDN], recorded[FQDN], domain_zone_id[domain_name])