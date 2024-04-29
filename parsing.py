import json, os, time

json_string = os.environ["HOSTS"]

json_object = json.loads(json_string)
formatted_json_string = json.dumps(json_object, indent=2)
print(formatted_json_string)

time.sleep(20)
