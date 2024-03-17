import requests, time, json, os, socket
from cloudflare_dns import find_record, delete_record, add_record

dns_cache = {}

# override the default dns resolver that requests.get calls under the hood
prv_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args):
    if args[0] in dns_cache:
        return prv_getaddrinfo(dns_cache[args[0]], *args[1:])
    else:
        return prv_getaddrinfo(*args)
socket.getaddrinfo = new_getaddrinfo


# this needs to be in the loop
subdomain = "alvin-test"

ip_addr_list = os.environ["IP_ADDR_LIST"].split(',') if os.environ["IP_ADDR_LIST"] else []
length = len(ip_addr_list)
recorded = [find_record(ip_addr_list[i])[1] for i in range(len(ip_addr_list))]
uptime = [0] * length
downtime = [0] * length

# url needs to be a list
url = os.environ["URL"]
get_timeout = int(os.environ["GET_TIMEOUT"])
up_num = int(os.environ["UP_NUM"])
down_num = int(os.environ["DOWN_NUM"])
cloudflare_watcher_num = int(os.environ["CLOUDFLARE_WATCHER_NUM"])
count = 0

while True:
    count += 1
    if count == cloudflare_watcher_num:
        # protection against accidental manual deletion of the record on the cloudflare dashboard
        count = 0
        recorded = [find_record(ip_addr_list[i])[1] for i in range(len(ip_addr_list))]
    for i in range(len(ip_addr_list)):
        try:
            dns_cache[url] = ip_addr_list[i]
            response = requests.get(f"http://{url}:8080", timeout=get_timeout)
            print(f"node{i} UP")
            uptime[i] += 1
            downtime[i] = 0
            if not recorded[i] and uptime[i] >= up_num:
                # add record to cloudflare dns recordbook
                success = add_record(ip_addr_list[i], subdomain)
                if success:
                    print(f"node{i} ADD SUCCESSFUL")
                    recorded[i] = True
                else:
                    print(f"node{i} ADD FAILED")
                uptime[i] == 0
        except:
            # failed connection (node is potentially down)
            print(f"node{i} NO ANSWER")
            uptime[i] = 0
            downtime[i] += 1
            if downtime[i] == down_num:
                # find dns id of the host
                record_id, found = find_record(ip_addr_list[i])
                if found:
                    # delete record from cloudflare dns recordbook
                    success = delete_record(record_id)
                    if success:
                        recorded[i] = False
                        print(f"node{i} DELETE SUCCESSFUL")
                    else:
                        print(f"ATTENTION: couldn't delete node{i} with its record id")
                else:
                    print(f"record id of node{i} cannot be found on cloudflare")
                downtime[i] = 0
    time.sleep(2)
