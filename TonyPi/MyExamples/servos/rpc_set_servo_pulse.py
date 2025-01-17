import requests
import json


def main():
    url = "http://192.168.1.52:9030/jsonrpc"
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": "GetBusServosDeviation",
        "params": ["readDeviation"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    print(response["result"][1])      
    # print(response["jsonrpc"])
    # print(response["id"])

if __name__ == "__main__":
    main()