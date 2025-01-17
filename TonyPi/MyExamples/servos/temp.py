# Settings [deviation, temperature_limit, position, pos_min, pos_max, vin_min, vin_max]
servos_settings = [
    [0, 60, 500, 0, 1000, 4500, 14000], # servoId = 0 doesn't exist
    [0, 60, 500, 0, 1000, 4500, 14000], # servoId = 1 
    [0, 60, 500, 0, 1000, 4500, 12500], # servoId
]

def run(name, servoId=-1, deviation=0, temp=85, pos=499, pos_min=0, pos_max=1000, vin_min=4.5, vin_max=14):
    print(f'name={name}')
    print(f'servoId={servoId}')
    print(f'deviation={deviation}')
    print(f'position={pos}')
    print(f'vin_max={vin_max}')


servoId = 2
print(servos_settings[servoId])
deviation, temp, pos, pos_min, pos_max, vin_min, vin_max = servos_settings[servoId]
run('test servoId 2', 33, deviation, temp, pos, pos_min, pos_max, vin_min, vin_max)