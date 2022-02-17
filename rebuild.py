import json
import json
import random
import string
import sys
import time

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound, serverbound, PositionAndLookPacket, PlayerPositionAndLookPacket

class MainPlayer:
    def __init__(self, options, auto_revive=False):
        self.name = options['username']
        self.x = None
        self.y = None
        self.z = None
        self.yaw = None
        self.pitch = None
        self.health = None
        self.hunger = None
        self.connection = self.connect(options)
        self.location_position_update_method()
        if auto_revive:
            self.auto_revive_method()

        time.sleep(5)
        self.move()


    def connect(self, options):
        if options['offline']:
            print("Connecting in offline mode...")
            connection = Connection(
                options['host'],
                options['port'],
                username=options['username']
            )
        else:
            auth_token = authentication.AuthenticationToken()
            try:
                auth_token.authenticate(options['username'], options['password'])
            except YggdrasilError as e:
                print(e)
                sys.exit()
            print(f"Logged in as {auth_token.username}")
            connection = Connection(
                options['host'], options['port'], auth_token=auth_token)

        try:
            connection.connect()
        except ConnectionRefusedError:
            print("Connection refused: either the port is wrong or it doesn't exist")
            sys.exit()
        except TimeoutError:
            print("Connection timed out: either the server is lagging or it doesn't exist")
            sys.exit()

        return connection

    def auto_revive_method(self):
        def respawn_listener(chat_packet):
            if json.loads(chat_packet.json_data)['translate'] == 'death.attack.player':
                packet = serverbound.play.ClientStatusPacket()
                packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                self.connection.write_packet(packet)
        self.connection.register_packet_listener(respawn_listener, clientbound.play.ChatMessagePacket)

    def location_position_update_method(self):
        def location_position_update_listener(packet):
            print(packet)
            self.x = packet.x
            self.y = packet.y
            self.z = packet.z
            self.yaw = packet.yaw
            self.pitch = packet.pitch
        self.connection.register_packet_listener(location_position_update_listener, PlayerPositionAndLookPacket)


    def move(self):
        while True:
            self.x += 0.43
            self.z += 0.43
            time.sleep(0.1)
            packet = serverbound.play.PositionAndLookPacket()
            packet.x = self.x
            packet.feet_y = self.y
            packet.z = self.z
            packet.yaw = self.yaw
            packet.pitch = self.pitch
            packet.on_ground = True
            self.connection.write_packet(packet)

def main():

    options = {
        'offline': True,
        'username': ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        'password': '', # keep blank if offline is True
        'host': 'localhost',
        'port': 2663,
    }

    player = MainPlayer(
        options=options,
        auto_revive=True
    )

    while True:
        time.sleep(1)
        pass

if __name__ == "__main__":
    main()