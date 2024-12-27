import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dynamic_cli_builder import load_config, build_cli

class TestDynamicCLI(unittest.TestCase):
    def test_load_config(self):
        config = load_config("config.yaml")
        self.assertIn("commands", config)
        for command in config["commands"]:
            self.assertIn("name", command)
            self.assertIn("description", command)
            self.assertIn("action", command)
            self.assertIn("args", command)
            self.assertIn("action", command)
    
    def test_build_cli(self):
        config = {
            "description": "Test CLI",
            "commands": [
                {"name": "greet", "description": "Greet someone", "args": [{"name": "name", "type": "str", "help": "Name"}]}
            ]
        }
        parser = build_cli(config)
        self.assertIsNotNone(parser)

if __name__ == "__main__":
    unittest.main()