import threading
import subprocess
import websockets
import json
import asyncio
import hiwonder.ActionGroupControl as AGC

async def call_rpc(method, params=None):
    websocket = None
    try:
        websocket = await websockets.connect('ws://192.168.1.52/up')
        call = dict(jsonrpc='2.0', method=method)
        if params is not None:
            call['params'] = params
#            logger.debug(json.dumps(call))
        await websocket.send(json.dumps(call))
        await websocket.close()
    except Exception as e:
#         logger.error(e)
        if websocket is not None:
            await websocket.close()

async def run_action_set(action_set_name, repeat):
    await call_rpc('run_action_set', [action_set_name, repeat])

async def stop(action_set_name=None):
    await call_rpc('stop')
    if action_set_name is not None:
        await run_action_set(action_set_name, 1)

#shield = True
th = None
#last_status = ''
connected = False
times = 1



try:
    actName = 'right_kick'
    print("right_kick")

    asyncio.run(run_action_set(actName, 1))
    th = threading.Thread(target=AGC.runActionGroup, args=(actName, times), daemon=True)
    th.start()
except Exception as e:
    print(e)
    connected = False          



# subprocess.Popen("python3 /home/pi/TonyPi/Extend/athletics_course/athletics_perform.py",shell=True)
#                     time.sleep(1)

# board.set_buzzer(1900, 0.1, 0.9, 1) # at a frequency of 1900Hz, beep for 0.1 seconds, then silence for 0.9 seconds, repeating once


