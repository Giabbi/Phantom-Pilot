import paramiko
from threading import Thread
from time import sleep
from turtle import Screen, Turtle, done
from queue import Queue

screen = Screen()
screenTk = screen.getcanvas().winfo_toplevel()
screen.title("Phantom Pilot")
screen.tracer(0)
# In this case, the background picture is on the desktop, on a reall app the bg would be in the same folder as the program
screen.bgpic(picname="C:\\Users\\Giabbi\\Desktop\\bg.gif") 

commandQueue = Queue() # Queue to process turtle comands in the main tread since tkinter is not Thread safe

writeEvents = Turtle() # Create a pen to write events on the screen
writeEvents.hideturtle()
writeEvents.penup()
writeEventsY = 200
writeEvents.goto(-250, writeEventsY)


global shell1, shell2, car2Finish, car1Finish
shell1 = False
shell2 = False
car2Finish = False
car1Finish = False

def create_turtle(shape):
    t = Turtle(shape)
    return t

def car1Handler(dimensions, luck, nitro, power):
    global writeEventsY
    jump = True
    while True:
        if jump:
            car1 = paramiko.SSHClient() # Create SSH object
            car1.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Add auto add policy for new hosts
            car1.connect(username = "giabbi", hostname = "Giabbi.local", password = "mypi123") # SSH into Car 1's pi
            stdin, stdout, stderr = car1.exec_command("cd \"bcm2835-1.70/Motor_Driver_HAT_Code/Motor_Driver_HAT_Code/Raspberry Pi/python\"\npython3 main.py " + 
                                                      str(dimensions) + " " + str(luck) + " " + str(nitro) + " " + str(power), 
                                                      get_pty = True) # Change directory and start the program in car 1, get_pty = True is to reduce lag
            jump = False
            
        for line in iter(stdout.readline, ""): # Read bytes as they are sent from Car 1 
            global shell1
            if shell1 and "Car 2 got a power star! It has become invulnerable to crashes!" not in line: # Check if a shell has been thrown and if the current car has a power star
                stdin1, stdout1, stderr2 = car1.exec_command("cd \"bcm2835-1.70/Motor_Driver_HAT_Code/Motor_Driver_HAT_Code/Raspberry Pi/python\"\n python3 test.py", get_pty = True) # Test.py is stop.py, executing it kills the car for a few seconds
                jump = True # Restart SSH connection
                car1.close()
                break
        
            if "A shell was thrown by Car 1 to Car 2!" in line:
                shell2 = True # Throw the shell to Car 2
                
            commandQueue.put(lambda: writeEvents.write(line, align = "center", font = ("Britannic Bold", 10, "normal"))) # Write the events on the screen
            commandQueue.put(lambda: screen.update())
            if writeEventsY > -100:
                writeEventsY -= 30
                commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY)) # Move the next event to prevent overlapping
            else:
                commandQueue.put(lambda: writeEvents.clear()) # If events have gone too much down then clear the past events and bring the pen up
                writeEventsY = 200
                commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY))

            if "Car 1 crashed!!!" in line: # Check if the car crashed, on a crash a box would appear and the user has to click it, afterwards paramiko would re-run the program on the rpi
                print("Quick! Fix Car 1 before Car 2 wins, click the blue box to fix")
                restart = Turtle("square")
                commandQueue.put(lambda: restart.penup())
                commandQueue.put(lambda: restart.color("blue"))
                commandQueue.put(lambda: restart.goto(200, 50))
                commandQueue.put(lambda: screen.update())
                commandQueue.put(lambda: restart.onclick())
                commandQueue.put(lambda: writeEvents.write("Restarting Car 1...", align = "center", font = ("Britannic Bold", 10, "normal")))
                commandQueue.put(lambda: screen.update())
                if writeEventsY > -100:
                    writeEventsY -= 30
                    commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY)) # Move the next event to prevent overlappi
                else:
                    commandQueue.put(lambda:  writeEvents.clear())
                    writeEventsY = 200
                    commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY)) # If events have gone too much down then clear the past events and bring the pen up
                jump = True # Jump at the beginning of the loop and restart the SSH connection
            elif "Car 1 finished the race!" in line:
                global car1Finish
                car1Finish = True
                car1.close() # Close SSH connection
                return # Return Thread when the car finishes the race


def car2Handler(dimensions, luck, nitro, power):
    global writeEventsY
    jump = True
    while True:
        if jump:
            car2 = paramiko.SSHClient() # Create SSH object
            car2.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Add auto add policy for new hosts
            car2.connect(username = "giabbi", hostname = "ambropi.local", password = "Limatola1!") # SSH into Car 2's pi
            stdin, stdout, stderr = car2.exec_command("cd \"bcm2835-1.70/Motor_Driver_HAT_Code/Motor_Driver_HAT_Code/Raspberry Pi/python\"\npython3 main.py " + 
                                                      str(dimensions) + " " + str(luck) + " " + str(nitro) + " " + str(power), 
                                                      get_pty = True) # Change directory and start the program in car 2, get_pty = True is to reduce lag
            jump = False

        for line in iter(stdout.readline, ""): # Read bytes as they are sent from Car 2 
             global shell2
            if shell2 and "Car 2 got a power star! It has become invulnerable to crashes!" not in line: # Check if a shell has been thrown and if the current car has a power star
                stdin1, stdout1, stderr2 = car2.exec_command("cd \"bcm2835-1.70/Motor_Driver_HAT_Code/Motor_Driver_HAT_Code/Raspberry Pi/python\"\n python3 test.py", get_pty = True) # Test.py is stop.py here on github, executing it kills the car for a few seconds
                jump = True # Restart SSH connection
                car2.close()
                break 

            if "A shell was thrown by Car 2 to Car 1!" in line:
                shell1 = True # Throw the shell to Car 1

            # The following part is identical to car 1, for comments check car1Handler()
            commandQueue.put(lambda: writeEvents.write(line, align = "center", font = ("Britannic Bold", 10, "normal")))    
            commandQueue.put(lambda: screen.update())
            if writeEventsY > -100:
                writeEventsY -= 30
                commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY))
            else:
                commandQueue.put(writeEvents.clear())
                writeEventsY = 200
                commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY))

            if "Car 2 crashed!!!" in line: 
                print("Quick! Fix Car 2 before Car 1 wins, click the green box to fix")
                restart = Turtle("square")
                commandQueue.put(lambda: restart.penup())
                commandQueue.put(lambda: restart.color("green"))
                commandQueue.put(lambda: restart.goto(200, -50))
                commandQueue.put(lambda: screen.update())
                commandQueue.put(lambda: restart.onclick())
                commandQueue.put(lambda: writeEvents.write("Restarting Car 2...", align = "center", font = ("Britannic Bold", 15, "normal")))
                commandQueue.put(lambda: screen.update())
                if writeEventsY > -100:
                    writeEventsY -= 30
                    commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY - 30))
                else:
                    commandQueue.put(lambda: writeEvents.clear())
                    writeEventsY = 200
                    commandQueue.put(lambda: writeEvents.goto(-250, writeEventsY))
                jump = True 
            elif "A shell was thrown by Car 2 to Car 1!" in line:
                global shell1
                shell1 = True
            elif "Car 2 finished the race!" in line:
                global car2Finish
                car2Finish = True
                car2.close()
                return
            
def process_queue():
    while not commandQueue.empty():
        command = commandQueue.get()
        command()


def main():
    # Car 1 attributes prompts
    
    dimensions1 = int(screen.numinput("Select attributes for Car 1", "Choose the dimension for the car, 1 = very small 10 = the biggest",
                                       minval = 1, maxval = 10))
    if dimensions1 == None:
        screen.bye()

    luck1 = int(screen.numinput("Select attributes for Car 1", "Choose the luck for the car, 1 = unlucky but consistent 10 = lucky but umpredictable",
                                minval = 1, maxval = 10))
    if luck1 == None:
        screen.bye()
    
    nitro1 = int(screen.numinput("Select attributes for Car 1", "Choose the nitro for the car, 1 = no nitro but more overall speed 10 = less speed but high chance for nitro boost",
                                minval = 1, maxval = 10))
    if nitro1 == None:
        screen.bye()

    power1 = int(screen.numinput("Select attributes for Car 1", "Choose the power of the car, 1 = slower but less chance to crash 10 = faster but more chance to crash",
                                  minval = 1, maxval = 10))
    if power1 == None:
        screen.bye() 

    # Car 2 attribuites prompts
    
    dimensions2 = int(screen.numinput("Select attributes for Car 2", "Choose the dimension for the car, 1 = very small 10 = the biggest",
                                       minval = 1, maxval = 10))
    if dimensions2 == None:
        screen.bye()
    
    luck2 = int(screen.numinput("Select attributes for Car 2", "Choose the luck for the car, 1 = unlucky but consistent 10 = lucky but umpredictable",
                                minval = 1, maxval = 10))
    if luck2 == None:
        screen.bye()
    
    nitro2 = int(screen.numinput("Select attributes for Car 2", "Choose the nitro for the car, 1 = no nitro but more overall speed 10 = less speed but high chance for nitro boost",
                                minval = 1, maxval = 10))
    if nitro2 == None:
        screen.bye()
    
    power2 = int(screen.numinput("Select attributes for Car 2", "Choose the power of the car, 1 = slower but less chance to crash 10 = faster but more chance to crash",
                                  minval = 1, maxval = 10))
    if power2 == None:
        screen.bye() 

    # Create Car Threads
    car1Thread = Thread(target = car1Handler, args = (dimensions1, luck1, nitro1, power1), daemon=True)
    car2Thread = Thread(target = car2Handler, args = (dimensions2, luck2, nitro2, power2), daemon=True)

    # Start the two cars at the same time
    car1Thread.start()
    car2Thread.start()

    # Create a ready, set, go traffic light; the timing of sleep() was calculated according to my and the school's internet speed
    ready = Turtle()
    ready.penup()
    ready.goto(-200, 60)
    ready.pendown()
    ready.write("Ready?", align = "center", font = ("Britannic Bold", 15, "normal"))
    ready.penup()
    ready.goto(-200, 0)
    ready.shape("circle")
    ready.color("red")
    ready.shapesize(5,5,1)
    
    screen.update()


    sleep(4)

    set = Turtle()
    set.penup()
    set.goto(0, 60)
    set.pendown()
    set.write("Set?", align = "center", font = ("Britannic Bold", 15, "normal"))
    set.penup()
    set.goto(0, 0)
    set.shape("circle")
    set.color("yellow")
    set.shapesize(5,5,1)

    screen.update()

    sleep(4)

    go = Turtle()
    go.penup()
    go.goto(200, 60)
    go.pendown()
    go.write("GO!!!", align = "center", font = ("Britannic Bold", 15, "normal"))
    go.penup()
    go.goto(200, 0)
    go.shape("circle")
    go.color("green")
    go.shapesize(5,5,1)
    
    screen.update()

    sleep(1)

    # Clear traffic light for writeEvents Turtle
    ready.clear()
    ready.hideturtle()
    set.clear()
    set.hideturtle()
    go.clear()
    go.hideturtle()

    screen.update()

    global car1Finish, car2Finish
    while not car1Finish and not car2Finish: # Process the Queue in the main Threads with Turtle commands from both Car threads until both car finish the race
        process_queue()

    # Wait until both Threads return
    car1Thread.join()
    car2Thread.join()
    done()
    screen.bye() # When the race is over allow the user to close the screen

if __name__ == "__main__":
    main()
