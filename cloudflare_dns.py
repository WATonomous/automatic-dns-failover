#!/usr/bin/python3
# cloudflare_dns.py

import requests, json, os

def find_record(ip_addr, zone_id):
    # finds the record with the corresponding ip_addr and
    # returns the record id and the status of the operation
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": f"{os.environ['EMAIL']}",
        "X-Auth-Key": f"{os.environ['API_KEY']}"
    }
    
    found = False
    record_id = ""
    response = requests.request("GET", url, headers=headers).json()
    
    if response["success"]:
        for record in response["result"]:
            if record["content"]==ip_addr and record["type"]=="A":
                record_id = record["id"]
                found = True
                break
    
    return (record_id, found)

def delete_record(record_id, zone_id):
    # deletes the record with record_id

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": f"{os.environ['EMAIL']}",
        "X-Auth-Key": f"{os.environ['API_KEY']}"
    }
    
    response = requests.request("DELETE", url, headers=headers).json()
    if response["success"]:
        return True
    else:
        return False

def add_record(ip_addr, subdomain, zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    payload = {
        "content": f"{ip_addr}",
        "name": subdomain,
        "type": "A"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": f"{os.environ['EMAIL']}",
        "X-Auth-Key": f"{os.environ['API_KEY']}"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers).json()
    return response["success"]
    

def find_zones_under_account():
    # returns a dictionary of domain name: zone_id

    url = "https://api.cloudflare.com/client/v4/zones"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['API_TOKEN']}"
    }
    
    response = requests.request("GET", url, headers=headers).json()
    
    domain_dict = []
    if response["success"]:
        domain_dict = {response["result"][i]["name"]: response["result"][i]["id"] for i in range(len(response["result"]))}
    
    return domain_dict
