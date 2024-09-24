import random
import time
import turtle

window = turtle.Screen()
window.tracer(0)
window.setup(0.5, 0.75)
window.bgcolor(0.2, 0.2, 0.2)
window.title("Space Invaders")

# Create laser cannon
cannon = turtle.Turtle()
cannon.penup()
cannon.color(1, 1, 1)
cannon.shape("square")
cannon.setposition(0, -200)  # Initial cannon position
cannon.cannon_movement = 0  # -1 for left, 1 for right, 0 for stationary

# Game state variables
GAME_RUNNING = 0
lasers = []
power_lasers = []
aliens = []
power_activated = 0
power_activated_time = None
FRAME_RATE = 30
TIME_FOR_1_FRAME = 1 / FRAME_RATE
CANNON_STEP = 10
LASER_LENGTH = 20
LASER_SPEED = 20
ALIEN_SPAWN_INTERVAL = 1.2
ALIEN_SPEED = 3.5
LIFE = 3

LEFT = -window.window_width() / 2
RIGHT = window.window_width() / 2
TOP = window.window_height() / 2
BOTTOM = -window.window_height() / 2
FLOOR_LEVEL = 0.9 * BOTTOM
GUTTER = 0.025 * window.window_width()

def draw_cannon():
    cannon.clear()
    cannon.turtlesize(1, 4)  # Base
    cannon.stamp()
    cannon.sety(FLOOR_LEVEL + 10)
    cannon.turtlesize(1, 1.5)  # Next tier
    cannon.stamp()
    cannon.sety(FLOOR_LEVEL + 20)
    cannon.turtlesize(0.8, 0.3)  # Tip of cannon
    cannon.stamp()
    cannon.sety(FLOOR_LEVEL)

def move_left():
    cannon.cannon_movement = -1

def move_right():
    cannon.cannon_movement = 1

def stop_cannon_movement():
    cannon.cannon_movement = 0

def create_laser():
    if power_activated == 1:
        if power_activated_time is not None and (time.time() - power_activated_time <4)  :
            return power_laser()
    laser = turtle.Turtle()
    laser.penup()
    laser.color(1, 0, 0)
    laser.hideturtle()
    laser.setposition(cannon.xcor(), cannon.ycor() + 10)
    laser.setheading(90)
    laser.pendown()
    laser.pensize(5)
    lasers.append(laser)

def activate_power1():
    global power_activated, power_activated_time
    power_activated_time = time.time()
    if power_activated == 0:
        power_activated = 1
    elif power_activated == 1:
        power_activated = 0

def power_laser():
    laser = turtle.Turtle()
    laser.penup()
    laser.color(0, 1, 0)
    laser.shape("circle")  # Set the shape first
    laser.shapesize(stretch_wid=0.5, stretch_len=4)  # Adjust the size
    laser.hideturtle()
    laser.setposition(cannon.xcor(), cannon.ycor() + 10)
    laser.setheading(90)
    # laser.pendown()
    laser.showturtle()  # Show the laser after positioning
    power_lasers.append(laser)


def move_laser(laser):
    laser.clear()
    laser.forward(LASER_SPEED)
    if laser.ycor() > TOP:
        if laser in lasers:
            remove_sprite(laser, lasers)
        elif lasers in power_lasers:
            remove_sprite(laser, power_lasers)

def create_alien():
    alien = turtle.Turtle()
    alien.penup()
    alien.turtlesize(1.5)
    alien.setposition(random.randint(int(LEFT + GUTTER), int(RIGHT - GUTTER)), TOP)
    alien.shape("turtle")
    alien.setheading(-90)
    alien.color('white')
    aliens.append(alien)

def remove_sprite(sprite, sprite_list):
    sprite.clear()
    sprite.hideturtle()
    window.update()
    sprite_list.remove(sprite)

def game_play():
    global LIFE, GAME_RUNNING, lasers, aliens
    window.clear()
    window.tracer(0)
    window.bgcolor(0.2, 0.2, 0.2)
    LIFE = 3
    score = 0
    lasers.clear()
    aliens.clear()
    GAME_RUNNING = 0
    cannon.setposition(0, FLOOR_LEVEL)
    cannon.cannon_movement = 0

    # Create turtle for writing text
    text = turtle.Turtle()
    text.penup()
    text.hideturtle()
    text.setposition(LEFT * 0.8, TOP * 0.7)
    text.color(1, 1, 1)

    # Key bindings
    window.onkeypress(move_left, "Left")
    window.onkeypress(move_right, "Right")
    window.onkeyrelease(stop_cannon_movement, "Left")
    window.onkeyrelease(stop_cannon_movement, "Right")
    window.onkeypress(create_laser, "space")
    window.onkeypress(activate_power1, "p")
    window.onkeypress(turtle.bye, "q")
    window.listen()

    draw_cannon()

    # Game loop
    alien_timer = 0
    game_timer = time.time()

    while LIFE > 0:
        window.update()
        time_elapsed = time.time() - game_timer
        text.clear()
        text.write(f"Time: {time_elapsed:5.1f}s\nScore: {score:5}\nLife: {LIFE}", font=("Courier", 20, "bold"))

        # Move cannon
        new_x = cannon.xcor() + CANNON_STEP * cannon.cannon_movement
        if LEFT + GUTTER <= new_x <= RIGHT - GUTTER:
            cannon.setx(new_x)
            draw_cannon()

        # Move all lasers
        for laser in lasers.copy():
            move_laser(laser)

        # Spawn new aliens
        if time.time() - alien_timer > ALIEN_SPAWN_INTERVAL:
            create_alien()
            alien_timer = time.time()

        # Move all aliens
        # Move all aliens
        for alien in aliens.copy():
            alien.forward(ALIEN_SPEED)

            # Prepare to remove lasers
            lasers_to_remove = []
            power_lasers_to_remove = []

            # Check for collision with normal lasers
            for laser in lasers.copy():
                if laser.distance(alien) < 20:
                    lasers_to_remove.append(laser)
                    remove_sprite(alien, aliens)
                    score += 1

            # Check for collision with power lasers
            for laser in power_lasers.copy():
                move_laser(laser)
                if laser.ycor() > TOP:
                    power_lasers_to_remove.append(laser)
                    continue  # Skip to the next laser

                # Check if they are on the same y level
                if abs(laser.ycor() - alien.ycor()) < 20:
                    if abs(laser.xcor() - alien.xcor()) < 50:  # Define your threshold
                        power_lasers_to_remove.append(laser)
                        remove_sprite(alien, aliens)
                        score += 1

            # Remove lasers after the loop to avoid modifying the list during iteration
            for laser in lasers_to_remove:
                remove_sprite(laser, lasers)

            for laser in power_lasers_to_remove:
                remove_sprite(laser, power_lasers)

            if alien.ycor() < FLOOR_LEVEL:
                LIFE -= 1
                remove_sprite(alien, aliens)

        time.sleep(TIME_FOR_1_FRAME)

    # Game Over
    GAME_RUNNING = 1
    game_over_screen()

def game_over_screen():
    global window
    window.clear()
    window.bgcolor(0.2, 0.2, 0.2)
    splash_text = turtle.Turtle()
    splash_text.penup()
    splash_text.hideturtle()
    splash_text.color(1, 1, 1)
    splash_text.setposition(LEFT * 0.38, TOP * 0.3)
    splash_text.write("GAME OVER", font=("Courier", 40, "bold"))

    play_again_text = turtle.Turtle()
    play_again_text.penup()
    play_again_text.hideturtle()
    play_again_text.setposition(LEFT * 0.4, TOP * 0.1)
    play_again_text.write("Click to Play Again", font=("Courier", 20, "bold"))

    window.onclick(play_again)

def play_again(x, y):
    game_play()

# Start the game
game_play()

turtle.done()
