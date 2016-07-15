import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename="unittest.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestCisco(unittest.TestCase):
    @staticmethod
    def load_credits():
        config_path = 'config.yaml'
        config = yaml.load(open(config_path, 'r'))
        devices = yaml.load(open(config['device_credentials'], 'r'))
        params = [p for p in devices if p['device_type'] == 'hp_comware']
        return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_sysname(self):
        async def task():
            for dev in self.devices:
                hp = netdev.connect(**dev)
                await hp.connect()
                out = await hp.send_command('display cur | i sysname')
                self.assertIn("sysname", out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                hp = netdev.connect(**dev)
                await hp.connect()
                commands = ["dir", "display ver", "display cur", "display ssh server status"]
                for cmd in commands:
                    out = await hp.send_command(cmd, strip_command=False)
                    self.assertIn(cmd, out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                hp = netdev.connect(**dev)
                await hp.connect()
                commands = ["vlan 1", "quit"]
                out = await hp.send_config_set(commands)
                self.assertIn("vlan 1", out)
                self.assertIn("quit", out)
                await hp.disconnect()

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                hp = netdev.connect(**dev)
                await hp.connect()
                out = await hp.send_command('display cur | i sysname')
                self.assertIn(hp.base_prompt, out)
                await hp.disconnect()

        self.loop.run_until_complete(task())