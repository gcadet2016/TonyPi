import requests
import json
import time

url = "http://192.168.1.52:9030/jsonrpc"
headers = {'content-type': 'application/json'}

right_arm_position = 0
left_arm_position = 0


def get_bus_servo_deviation():
    global url, headers

    print("Bus servo deviation:")
    payload = {
        "method": "GetBusServosDeviation",
        "params": ["readDeviation"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(response["result"][1])      

def get_bus_servo_pulse():
    global url, headers, right_arm_position, left_arm_position

    print("Bus servo pulse:")
    payload = {
        "method": "GetBusServosPulse",
        "params": ["angularReadback"],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(response["result"][1])  
    right_arm_position = response["result"][1][7] 
    left_arm_position = response["result"][1][14]

def move_arms(pos_right, pos_left, delta):

    print("move_arms")
    payload = {
        "method": "SetBusServoPulse",
        "params": [1000, 2, 8, pos_right + delta, 16, pos_left - delta],
        #"params": [1000, 1, 16, pos_left + delta],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(response)  

# actionCode: string. Example '11'
# repeat: int. 0 = infinite loop
def RPC_RunAction_byCode(actionCode, repeat):
    payload = {
        "method": "RunAction",
        "params": [actionCode, repeat],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(f'RPC_RunAction_byCode result: {response["result"][2]}')
    assert response["result"][2] == "RunAction"     # No output, as the condition is True
    assert response["jsonrpc"]  
    assert response["id"] == 0

if __name__ == "__main__":
    RPC_RunAction_byCode('0',1)

    get_bus_servo_deviation()
    get_bus_servo_pulse()
    move_arms(right_arm_position, left_arm_position, -100)
    time.sleep(1)
    move_arms(right_arm_position, left_arm_position, -200)
    time.sleep(1)
    move_arms(right_arm_position, left_arm_position, 0)
# A tester
#  get_bus_servo_temp_limit