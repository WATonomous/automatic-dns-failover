#!/usr/bin/python3
# cloudflare_dns.py

import requests, json, os

def find_record(ip_addr, FQDN, zone_id):
    # finds the record with the corresponding ip_addr and
    # returns the record id and the status of the operation
    # notice that the parameter FQDN is not actually necessary
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"
    }
    
    found = False
    record_id = ""
    response = requests.request("GET", url, headers=headers).json()
    
    if response["success"]:
        count = response["result_info"]["count"]
        per_page = response["result_info"]["per_page"]
        total_pages = int(count/per_page) + (count%per_page>0)
        for i in range(1, total_pages+1):
            response = requests.request("GET", url+f"?page={i}", headers=headers).json()
            for record in response["result"]:
                if record["content"]==ip_addr and record["type"]=="A" and record["name"]==FQDN:
                    record_id = record["id"]
                    found = True
                    break
    
    return (record_id, found)

def delete_record(record_id, zone_id):
    # deletes the record with record_id

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"
    }
    
    response = requests.request("DELETE", url, headers=headers).json()
    return response["success"]

def add_record(ip_addr, subdomain, zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    payload = {
        "content": f"{ip_addr}",
        "name": subdomain,
        "type": "A"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"
    }
    
    response = requests.request("POST", url, json=payload, headers=headers).json()
    return response["success"]
    

def find_zones_under_account():
    # returns a dictionary of domain name: zone_id

    url = "https://api.cloudflare.com/client/v4/zones"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"
    }
    
    response = requests.request("GET", url, headers=headers).json()
    if response["success"]:
        domain_dict = {}
        count = response["result_info"]["count"]
        per_page = response["result_info"]["per_page"]
        total_pages = int(count/per_page) + (count%per_page>0)
        for i in range(1, total_pages+1):
            response = requests.request("GET", url+f"?page={i}", headers=headers).json()
            result = response["result"]
            for j in range(len(result)):
                domain_dict[result[j]["name"]] = result[j]["id"]
    
    return domain_dict
