from panda3d.bullet import BulletWorld, BulletBoxShape, BulletRigidBodyNode, BulletCapsuleShape, ZUp
from panda3d.core import Vec3, TransformState, VBase3
from pkg_resources import non_empty_lines
from pubsub import pub
from game_object import GameObject
from player import Player

class GameWorld:
    def __init__(self, debugNode=None):
        self.properties = {}
        self.game_objects = {}

        self.next_id = 0

        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))


        if debugNode:
            self.physics_world.setDebugNode(debugNode)

        #avoids all of the if elses from last project
        self.kind_to_shape = {
            "player": self.create_capsule,
            "crate": self.create_box,
            "red_box": self.create_box,
            "enemy": self.create_capsule,
        }

    def create_capsule (self, position, size, kind, mass):
        radius = size[0]
        height = size[1]
        shape = BulletCapsuleShape(radius, height, ZUp)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0],position[1],position[2])))
        self.physics_world.attachRigidBody(node)
        return node

    def create_box (self, position, size, kind, mass):
        shape = BulletBoxShape(Vec3(size[0] / 2, size[1] / 2, size[2] / 2))
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0],position[1],position[2])))
        self.physics_world.attachRigidBody(node)
        return node
    def create_physics_object(self, position, kind, size, mass):
        if kind in self.kind_to_shape:
            return self.kind_to_shape[kind](position, size, kind, mass)
        raise ValueError(f"create_physics_object: invalid kind {kind}")
      #throw

    def create_object(self, position, kind, size,mass, subclass):
        #if kind == "player":
        #    obj = Player(position, kind, self.next_id, size)
        # else:
        #  obj = GameObject(position, kind, self.next_id, size)

        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, physics)
        self.next_id += 1
        self.game_objects[obj.id] = obj

        pub.sendMessage('create', game_object=obj)
        return obj

    def tick(self, dt):

        for id in self.game_objects:
            self.game_objects[id].tick()
            self.physics_world.do_physics(dt)

        # TODO: let the physics world get a tick in

    def load_world(self):
        self.create_object([0, 0, 0], "crate", (5,2,1),10, GameObject)
        self.create_object([0, -20, 0], "player", (0.1,0.8, 1), 10,Player)
        self.create_object([0, 0, -10], "crate", (50,50,1),0, GameObject)
        #mass of 0 , meaning the object should not move, static, will not drop with gravity

    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]

        return None

    def set_property(self, key, value):
        self.properties[key] = value
