import pyglet
import pyglet.graphics
from pyglet.gl import *
from pyglet.window import key
import random

from flowers import RedFlower, flower_classes

window = pyglet.window.Window()

stable_temp = 1
air_temps = [stable_temp] * window.width
air_conduction = 1
air_flow = 300 # Multiplier for updraft/downdrafts
air_thermal_mass = 1
solar_energy = 2

bodies = set()

class Body(pyglet.sprite.Sprite):
    def __init__(self, temp, albedo, emissivity, conduction, thermal_mass, *args, **kargs):
        super().__init__(*args, **kargs)
        self.temp = temp
        self.albedo = albedo
        self.emissivity = emissivity
        self.conduction = conduction
        self.thermal_mass = thermal_mass

    def draw(self):
        vertex_list = pyglet.graphics.vertex_list(8, 'v2f', 'c3B')
        vertex_list.vertices = [self.x, self.y,
                                self.x + self.width, self.y,
                                self.x + self.width, self.y + self.height,
                                self.x, self.y + self.height,
                                self.x + 1, self.y + 1,
                                self.x + self.width - 1, self.y + 1,
                                self.x + self.width - 1, self.y + self.height - 1,
                                self.x + 1, self.y + self.height - 1]
        color = temp_to_color(self.temp)
        vertex_list.colors = [0] * 12 + list(color) * 4
        vertex_list.draw(GL_QUADS)
        #super().draw()


butterfly = Body(stable_temp, 1, 0, 0.1, 0.001, pyglet.resource.image("resources/butterfly.png"))

butterfly.h_speed = 80
butterfly.v_speed = 20
butterfly.dx = 0
butterfly.dy = 0
butterfly.user_dy = 0
butterfly.y = 40
butterfly.scale = 3

bodies.add(butterfly)

ground_img = pyglet.resource.image("resources/ground.png")
for i in range(0, window.width // ground_img.width):
    segment = Body(stable_temp, 0.3 + (0.3 * random.random() - 0.15), 0.95, 0.1, 1, ground_img)
    segment.x = 0 + i * ground_img.width
    bodies.add(segment)


def temp_to_color(temp):
    return (int((1.0 - (1.0 / (temp + 1))) * 0xFF), 0x00, int((1.0 / (temp + 1)) * 0xFF))

air = pyglet.image.create(window.width, 1).get_image_data()
if air.format != 'RGBA':
    raise Exception("Unexpected image format for image data, got " + ground.format)

def draw_air():
    data = bytearray(window.width * 4)
    for i in range(len(data) // 4):
        color = temp_to_color(air_temps[i])
        data[i*4 + 0] = color[0]
        data[i*4 + 1] = color[1]
        data[i*4 + 2] = color[2]
        data[i*4 + 3] = 0xFF
    air.set_data(air.format, window.width * 4, bytes(data))
    air.blit(0, 0, height=window.height)


@window.event
def on_draw():
    window.clear()
    draw_air()
    for body in bodies:
        body.draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.Q:
        window.close()
    if symbol == key.LEFT:
        butterfly.dx -= butterfly.h_speed
    if symbol == key.RIGHT:
        butterfly.dx += butterfly.h_speed
    if symbol == key.UP:
        butterfly.user_dy += butterfly.v_speed
    if symbol == key.DOWN:
        butterfly.user_dy -= butterfly.v_speed


@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.LEFT:
        butterfly.dx += butterfly.h_speed
    if symbol == key.RIGHT:
        butterfly.dx -= butterfly.h_speed
    if symbol == key.UP:
        butterfly.user_dy -= butterfly.v_speed
    if symbol == key.DOWN:
        butterfly.user_dy += butterfly.v_speed


def animation_update(dt):
    butterfly.x = (butterfly.x + butterfly.dx * dt)
    butterfly.y = (butterfly.y + (butterfly.dy + butterfly.user_dy) * dt)


def state_update(dt):
    update_temperatures(dt)
    update_butterfly()


def update_temperatures(dt):
    # Update temperatures
    
    top = [None] * window.width
    for body in bodies:
        for i in range(max(0, int(body.x)), min(len(air_temps), int(body.x + body.width))):
            if top[i] is None or body.y + body.height > top[i].y + top[i].height:
                top[i] = body

    # Absorb the solar radiation
    for body in top:
        if body is not None:
            body.temp += dt * solar_energy * (1 - body.albedo) / (body.width * body.thermal_mass)

    # Radiate excess energy into space
    for body in top:
        if body is not None:
            body.temp -= dt * body.temp * body.emissivity / (body.width * body.thermal_mass)

    # Conduct away heat to/from the air
    for body in bodies:
        for i in range(max(0, int(body.x)), min(len(air_temps), int(body.x + body.width))):
            delta = (body.temp**2 - air_temps[i]**2) * body.conduction * dt
            air_temps[i] += delta / air_thermal_mass
            body.temp -= delta / (body.width * body.thermal_mass)

    # Smooth out the heat in the air columns
    # FIXME: This is an O(n) with a large constant, but we could track the average and
    #        reduce the constant. Consider?
    offset = 20 # Distance either side to take the mean over
    means = [0.0] * len(air_temps)
    for i in range(len(air_temps)):
        lower = max(0, i - offset)
        upper = min(len(air_temps), i + offset)
        means[i] = sum(air_temps[j] for j in range(lower, upper)) / (upper - lower)
    for i, target in enumerate(means): air_temps[i] += (target - air_temps[i]) * dt * air_conduction


def update_butterfly():
    # Butterfly height changes depending on the air temp - kind of simulating an
    # updraft/downdraft.
    lower = int(max(0, butterfly.x))
    upper = int(min(window.width, butterfly.x + butterfly.width))
    butterfly_air_temp = sum(air_temps[i] for i in range(lower, upper)) / (upper - lower)
    mean_air_temp = sum(t for t in air_temps) / len(air_temps)
    butterfly.dy = (butterfly_air_temp - mean_air_temp) * air_flow


pyglet.clock.schedule_interval(animation_update, 1/60.0)
pyglet.clock.schedule_interval(state_update, 1/20.0)
pyglet.app.run()

