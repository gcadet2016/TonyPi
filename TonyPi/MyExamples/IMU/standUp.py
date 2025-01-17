# standUp.py
# Version 1.0
#
# Check if robot is down and stand up
# RPC call
#

import requests
import json

def main():
    url = "http://192.168.1.52:9030/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Invoke StandUp method
    payload = {
        "method": "StandUp",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    # assert response["result"] == "echome!"      # No output, as the condition is True
    # assert response["jsonrpc"]
    # assert response["id"] == 0

    print(response["result"])      
    print(response["jsonrpc"])
    print(response["id"])


if __name__ == "__main__":
    main()