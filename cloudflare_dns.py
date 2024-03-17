import requests, time, json, os

def find_record(ip_addr):
    # finds the record with the corresponding ip_addr and
    # returns the record id and the status of the operation
    
    url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['ZONE_ID']}/dns_records"
    
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

def delete_record(record_id):
    # deletes the record with record_id
    
    url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['ZONE_ID']}/dns_records/{record_id}"

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

def add_record(ip_addr, subdomain):
    url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['ZONE_ID']}/dns_records"

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
