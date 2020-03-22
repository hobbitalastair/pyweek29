import pyglet
from pyglet.window import key
import random

from flowers import RedFlower, flower_classes

window = pyglet.window.Window()
butterfly = pyglet.sprite.Sprite(pyglet.resource.image("resources/butterfly.png"))

butterfly.btn_speed = 80
butterfly.dx = 0
butterfly.dy = 0
butterfly.y = 40
butterfly.scale = 3

shaded = [0.0] * window.width
temps = [0.0] * window.width

flowers = {RedFlower(50)}

background = pyglet.image.create(*window.get_size(), pyglet.image.SolidColorImagePattern((255, 255, 255, 255)))
ground = pyglet.image.create(window.width, 1).get_image_data()
if ground.format != 'RGBA':
    raise Exception("Unexpected image format for image data, got " + ground.format)


def draw_temps():
    background.blit(0, 0)

    data = bytearray(window.width * 4)
    for i in range(len(data) // 4):
        data[i*4 + 0] = int(temps[i] * 0xFF)
        data[i*4 + 1] = 0x00
        data[i*4 + 2] = int((1.0 - temps[i]) * 0xFF)
        data[i*4 + 3] = 0xFF
    ground.set_data(ground.format, window.width * 4, bytes(data))
    
    ground.blit(0, 0, height=10)


@window.event
def on_draw():
    window.clear()
    draw_temps()
    for flower in flowers:
        flower.draw()
    butterfly.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.Q:
        window.close()
    if symbol == key.LEFT:
        butterfly.dx -= butterfly.btn_speed
    if symbol == key.RIGHT:
        butterfly.dx += butterfly.btn_speed


@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.LEFT:
        butterfly.dx += butterfly.btn_speed
    if symbol == key.RIGHT:
        butterfly.dx -= butterfly.btn_speed


def animation_update(dt):
    butterfly.x += butterfly.dx * dt
    butterfly.y += butterfly.dy * dt


def state_update(dt):
    # Update shade map
    for i in range(len(shaded)): shaded[i] = -1
    for sprite in flowers.union({butterfly}):
        for i in range(int(sprite.x), int(sprite.x + sprite.width)):
            if i in range(0, len(shaded)):
                shaded[i] = max(sprite.y, shaded[i])

    # Update temperatures
    for i, temp in enumerate(temps):
        if shaded[i] == -1:
            temps[i] = min(1, temp + (0.2 * dt))
        else:
            temps[i] = max(0, temp - (0.3 * dt))

    # Update existing plants
    dead = set()
    for sprite in flowers:
        avg = sum(temps[i] for i in range(int(sprite.x), int(sprite.x + sprite.width)) if i in range(0, len(temps))) / sprite.width
        if avg > sprite.max_temp or avg < sprite.min_temp:
            dead.add(sprite)
    flowers.difference_update(dead)

    # Seed plants
    for i, temp in enumerate(temps):
        for flower_class in flower_classes:
            if temp < flower_class.seed_max_temp and temp > flower_class.seed_min_temp:
                if random.random() > 0.99:
                    flowers.add(flower_class(i))
                


pyglet.clock.schedule_interval(animation_update, 1/60.0)
pyglet.clock.schedule_interval(state_update, 1/20.0)
pyglet.app.run()

