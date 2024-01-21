from multiprocessing.pool import ThreadPool
from random import randint
from sys import argv
from time import sleep
from threading import Thread

# The following code is from Waveshare's motor HAT documentation

from PCA9685 import PCA9685


Dir = [
    'forward',
    'backward',
]
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

class MotorDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def MotorRun(self, motor, index, speed):
        if speed > 100: # Cap speed to 100
            return
        if(motor == 0):
            pwm.setDutycycle(self.PWMA, speed)
            if(index == Dir[0]):
                print ("1")
                pwm.setLevel(self.AIN1, 0)
                pwm.setLevel(self.AIN2, 1)
            else:
                print ("2")
                pwm.setLevel(self.AIN1, 1)
                pwm.setLevel(self.AIN2, 0)
        else:
            pwm.setDutycycle(self.PWMB, speed)
            if(index == Dir[0]):
                print ("3")
                pwm.setLevel(self.BIN1, 0)
                pwm.setLevel(self.BIN2, 1)
            else:
                print ("4")
                pwm.setLevel(self.BIN1, 1)
                pwm.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        if (motor == 0):
            pwm.setDutycycle(self.PWMA, 0)
        else:
            pwm.setDutycycle(self.PWMB, 0) 

# The following code was written by Giancarlo

def killSwitch(): # Ends the program after 60 seconds
    sleep(60)
    global eventCode
    eventCode = -1
    return

def crash(power, luck, dimension):
    chance = 20 - power/2 - luck/2 + dimension # Power and luck increase chance of crashing by diminishing range of randint while dimension does the opposite
    if chance <= 0:
        chance = 1
    else:
        isCrashed = randint(0, int(chance*10))
        if isCrashed == 0:
            return True
        else:
            return False
        
def boost(luck, nitro):
    chance = (luck - 10) * -1 + (nitro - 10) *-1 # Nitro and luck increase chance of boost by diminishing range of randint 
    if chance <= 0:
        chance = 1
    isBoosted = randint(0, chance * luck)
    if isBoosted == 0:
        return True
    else:
        return False
    
def nerf(luck, dimension):
    chance = (luck - 10) * -1 + (dimension - 10) *-1 # Dimension and luck increase chance of slowing down by diminishing range of randint
    if chance <= 0:
        chance = 1
    isNerfed = randint(0, chance * luck)
    if isNerfed == 0:
        return True
    else:
        return False  
    
def carSpeed():
    # Update speed every 3 seconds
    sleep(3)
    global wasBoosted, wasNerfed, eventCode
    # Set appropriate eventCode and change speed based on randint results
    if crash(power, luck, dimensions) and eventCode != 3: 
        eventCode = 0
        return 0
    elif boost(luck, nitro) and nitro != 1:
        eventCode = 6
        if wasBoosted == False: 
            wasBoosted = True
            return speed + float(nitro)
        else:
            return speed
    elif nerf(luck, dimensions):
        eventCode = 7
        if wasNerfed == False:
            wasNerfed = True
            return speed - 15
        else:
            return speed
    else:
        if wasBoosted:
            wasBoosted = False
            return speed - float(nitro)
        elif wasNerfed:
            wasNerfed = False
            return speed + 15
        else:
            return speed
        
def luckyBlock():
    global speed, eventCode
    drop = 0
    for i in range (0, 10):
        sleep(8)
        if speed <= 0: # This if is to stop this thread once the race is over
            break
        if drop == 5: # This if is to reset speed after rocket
            speed -= 20
        if luck < 3: # This if is to handle ranges that are too small for randint
            drop = 1
        else:
            drop = randint(1, int(luck/2))
        match drop:
            case 1:
                # Power Mushroom
                eventCode = 1
                global dimensions
                dimensions = int(argv[1])
                dimensions += 10
            case 2: 
                # Power Star
                eventCode = 2
                global nitro
                nitro = int(argv[3])
                nitro += 10
            case 3:
                # Star
                eventCode = 3
            case 4:
                # Shell
                eventCode = 4
            case 5:
                # Rocket
                eventCode = 5
                speed += 20
    return

    
def main():  
    global dimensions, luck, nitro, power, wasBoosted, wasNerfed, speed, eventCode

    motor = MotorDriver() # Initialize motor object

    # Get attributes from command line arguments given by paramiko
    dimensions = int(argv[1])
    luck = int(argv[2])
    nitro = int(argv[3])
    power = int(argv[4])

    # Calculate speed based on attributes
    baseSpeed = 50
    speed = baseSpeed - float(dimensions) - float(nitro) + float(power)
    if speed < 25: # I set a minimum for speed because if it goes lower than 25 the car barely moves
        speed = 25
    elif speed > 100: # Checks if the speed is more than 100 and lowers it for demonstration
        speed = 100

    # Set control variables
    wasBoosted = False
    wasNerfed = False
    eventCode = 100

    # Start lucky block and killer Threads
    luckyBlockThread = Thread(target = luckyBlock)
    stopTimer = Thread(target = killSwitch)
    luckyBlockThread.start()
    stopTimer.start()

    # There is a try except only because this is a testing version, this control strcuture is not in the actual car
    try:
        while True:
            carPool = ThreadPool(processes = 1) # Initialize and start Thread for speed with ThreadPool so that I can get return value
            speedResults = carPool.apply_async(carSpeed)
            speed = speedResults.get() # Gets return values
            # Try to match event codes, if none just moves forward; After an event the event code is set back to base value of 100
            match eventCode:      
                case 0:
                    print("Car 1 crashed!!!")
                    motor.MotorStop(0)
                    motor.MotorStop(1)
                    return
                case -1:
                    print("Car 1 finished the race!")
                    speed = 0
                    motor.MotorStop(0)
                    motor.MotorStop(1)
                    return
                case 1:
                    print("Car 1  got a power mushroom, its size is increasing!")
                    eventCode = 100
                case 2:
                    print("The nitro of car 1 increased!")
                    eventCode = 100
                case 3:
                    print("Car 1 got a power star! It has become invulnerable to crashes!")
                    eventCode = 100
                case 4: 
                    print("A shell was thrown by Car 1 to Car 2!")
                    eventCode = 100
                case 5:
                    print("Car 1 rocket mode: ENGAGED!!!")
                    eventCode = 100
                case 6:
                    print("Car 1 nitro: activated!!!")
                    eventCode = 100
                case 7:
                    print("Car 1 is slowing down!")
                    eventCode = 100
                case _:
                    continue
            if speed > 100: # Check again for speed limits
                speed = 100
            elif speed < 25:
                speed = 25
            # Here it says backwards because I saw that with this keyword the car runs faster than with forward, 
            # to get the car to still go forward I simply switched the wiring of the motor driver
            motor.MotorRun(0, 'backward', speed) 
            motor.MotorRun(1, 'backward', speed)
    except KeyboardInterrupt:
        speed = 0
        print("User interrupted the car")

if __name__ == "__main__":
    main()
