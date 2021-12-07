import pymunk


class PhysicsManager:
    def __init__(self):
        self.space = PhysicsSpace()


class PhysicsSpace:
    def __init__(self):
        self.space = pymunk.Space()
        self.gravity = (0, -981)

    def add(self, *bodies):
        for body in bodies:
            self.space.add(body)


class Body:
    def __init__(self, mass=0, moment=0):
        self.body = pymunk.Body(mass, moment)

    def add(self, space):
        space.add(self.body)


class KinematicBody(Body):
    def __init__(self, mass=0, moment=0):
        super().__init__(mass, moment)
        self.body = pymunk.Body(mass, moment, pymunk.Body.KINEMATIC)


class StaticBody(Body):
    def __init__(self, mass=0, moment=0):
        super(StaticBody, self).__init__(mass, moment)
        self.body = pymunk.Body(mass, moment, pymunk.Body.STATIC)
