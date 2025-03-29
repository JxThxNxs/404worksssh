#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml

class CustomCommandsManager:
    def __init__(self):
        self.commands = []
        self.config_dir = os.path.join(os.path.expanduser("~"), ".sshworks")
        self.commands_file = os.path.join(self.config_dir, "commands.yaml")
        
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Load saved commands
        self.load_commands()
    
    def load_commands(self):
        """Load saved commands from file."""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, 'r') as f:
                    self.commands = yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading commands: {e}")
                self.commands = []
        else:
            self.commands = []
    
    def save_commands(self):
        """Save commands to file."""
        try:
            with open(self.commands_file, 'w') as f:
                yaml.dump(self.commands, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving commands: {e}")
    
    def get_all_commands(self):
        """Return all saved commands."""
        return self.commands
    
    def get_command(self, name):
        """Get a command by name."""
        for cmd in self.commands:
            if cmd["name"] == name:
                return cmd
        return None
    
    def add_command(self, command):
        """Add a new command."""
        # Check if command with same name already exists
        existing = self.get_command(command["name"])
        if existing:
            # Update existing command
            for i, cmd in enumerate(self.commands):
                if cmd["name"] == command["name"]:
                    self.commands[i] = command
                    break
        else:
            # Add new command
            self.commands.append(command)
        
        # Save to file
        self.save_commands()
    
    def remove_command(self, name):
        """Remove a command by name."""
        self.commands = [cmd for cmd in self.commands if cmd["name"] != name]
        self.save_commands()
