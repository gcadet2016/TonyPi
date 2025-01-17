# RunAction test
# Action list in C:\Users\guigu\OneDrive\Divers\IOT\TonyPi\CarteSD\home_pi folder\TonyPi\ActionGroupDict.py

import requests
import json

url = "http://192.168.1.52:9030/jsonrpc"
headers = {'content-type': 'application/json'}

action_dict = {
    'stand': '0' ,          # stand at attention
    'go_forward': '1',      # go forward
    'back_fast': '2',       # go backward
    'left_move_fast': '3',  # move to left
    'right_move_fast': '4', # move to right
    'push_ups': '5',        # push-up
    'sit_ups': '6',         # sit-up
    'turn_left': '7',       # turn left
    'turn_right': '8',      # turn right
    'wave': '9',            # wave
    'bow': '10',            # bow
    'squat': '11',          # squat
    'chest': '12',          # celebration
    'left_shot_fast': '13', # left kick
    'right_shot_fast': '14',# right kick
    'wing_chun': '15',      # Wing Chun = Signe 'viens' de la main droite 
    'left_uppercut': '16',  # left hook
    'right_uppercut': '17', # right hook
    'left_kick': '18',      # left kick
    'right_kick': '19',     # right kick
    'stand_up_front': '20', # front fall and stand up
    'stand_up_back': '21',  # backward fall and stand up
    'twist': '22',          # twist waist
    'stand_slow': '23',     # stand at attention
    'stepping': '24',       # march in place
    'jugong': '25',         # bow
    'weightlifting': '35'   # weightlifting
}

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

# actionCode: string. Example '11'
# repeat: int. 0 = infinite loop
def RPC_RunAction_byName(actionName, repeat):
    RPC_RunAction_byCode(action_dict[actionName], repeat)

def test_function():
    payload = {
        "method": "StandUp",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(f'StandUp function: {response["result"]}') 

def main():
    #RPC_RunAction_byCode('0',1)    # stand-up

    #RPC_RunAction_byName('wave', 1)
    #test_function()
    #RPC_RunAction_byName('go_forward', 5)
    test_function()
    # RPC_RunAction_byName('wing_chun', 5)
    #RPC_RunAction_byName('stand', 1)

if __name__ == "__main__":
    main()