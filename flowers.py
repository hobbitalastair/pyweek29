import pyglet

class Flower(pyglet.sprite.Sprite):
    def __init__(self, img, x, *args, **kargs):
        super().__init__(img, *args, **kargs)
        self.x = x
        self.y = 0


class RedFlower(Flower):

    img = pyglet.resource.image("resources/butterfly.png")
    seed_min_temp = 0.4
    seed_max_temp = 0.5
    min_temp = 0.2
    max_temp = 0.8

    def __init__(self, *args, **kargs):
        super().__init__(self.img, *args, **kargs)
        self.scale = 3


flower_classes = [RedFlower]

