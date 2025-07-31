import board
import busio
import displayio
import terminalio
from adafruit_st7789 import ST7789
import time
import random

displayio.release_displays()

tft_cs = board.GP28
tft_dc = board.GP27
#spi_mosi = board.GP22
#spi_miso = board.GP26
#spi_clk = board.GP21

print("Initializing SPI bus...")

# Increase SPI frequency for faster data transfer
spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)

print("Initializing display...")

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)

display = ST7789(display_bus, width=240, height=240, rowstart=80, rotation=90)
display.refresh()


def RandomizeVelocity():
    global ball_vel_x, ball_vel_y
    target_x = random.randrange(-200, 200)
    target_y = random.randrange(-200, 200)
    while target_x == target_y:
        target_x = random.randrange(-200, 200)
        target_y = random.randrange(-200, 200)
    ball_vel_x = target_x / 100
    ball_vel_y = target_y / 100


# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(240, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000 

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

squares = []
RandomizeVelocity()
ball_new_x = 0
ball_new_y = 0

inner_bitmap = displayio.Bitmap(5, 5, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xFFFFFF
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=120, y=120)
ball = inner_sprite
splash.append(inner_sprite)

def CreateSquare(x: int, y: int):
    inner_bitmap = displayio.Bitmap(5, 25, 1)
    inner_palette = displayio.Palette(1)
    inner_palette[0] = 0xFFFFFF
    inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=x, y=y)
    squares.append(inner_sprite)
    splash.append(inner_sprite)

CreateSquare(0, 0)

import analogio
import digitalio

y_joystick = analogio.AnalogIn(board.GP26)

z_switch = digitalio.DigitalInOut(board.GP18)
z_switch.direction = digitalio.Direction.INPUT
z_switch.pull = digitalio.Pull.UP

joystick_center = 32767  # Approximate center value for analog input
deadzone = 2000  # Ignore small movements near center
sensitivity = 0.00015  # Movement sensitivity (lower = slower)
movement_accumulator = 0.0  # For sub-pixel movement accuracy

while True:
    # Player Movement
    joystick_raw = y_joystick.value
    joystick_offset = joystick_raw - joystick_center
    
    if abs(joystick_offset) > deadzone:
        movement = joystick_offset * sensitivity
        movement_accumulator += movement
        
        if abs(movement_accumulator) >= 1.0:
            pixel_movement = int(movement_accumulator)
            movement_accumulator -= pixel_movement
            
            for square in squares:
                new_y = square.y + pixel_movement
                if 0 <= new_y <= 220:
                    square.y = new_y

    # Ball Movement

    if (ball.y >= 235):
        ball_vel_y += 0.2
        if ball_vel_y > 3:
            ball_vel_y = 3
        ball_vel_y = -ball_vel_y
        ball.y -= 5 

    if (0 >= ball.y):
        ball_vel_y -= 0.2
        if ball_vel_y < -3:
            ball_vel_y = -3
        ball_vel_y = -ball_vel_y
        ball.y += 5

    if (ball.x >= 235):
        ball_vel_x += 0.2
        if ball_vel_x > 3:
            ball_vel_x = 3
        ball_vel_x = -ball_vel_x
        ball.x -= 5

    if ball.x <= 0:
        if ball.y >= squares[0].y and ball.y <= squares[0].y + 25:
            ball_vel_x -= 0.2
            if ball_vel_x < -3:
                ball_vel_x = -3
            ball_vel_x = -ball_vel_x
            ball.x += 5
        else:
            RandomizeVelocity()
            ball.x = 120
            ball.y = 120
        

    if (abs(ball_new_x) >= 1.0):
        ball.x += round(ball_new_x)
        ball_new_x = 0

    if (abs(ball_new_y) >= 1.0):
        ball.y += round(ball_new_y)
        ball_new_y = 0

    ball_new_x += ball_vel_x
    ball_new_y += ball_vel_y

    display.refresh()
    time.sleep(0.02)