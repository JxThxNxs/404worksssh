#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import yaml
from pathlib import Path

class ConnectionManager:
    def __init__(self):
        self.connections = []
        self.config_dir = os.path.join(os.path.expanduser("~"), ".sshworks")
        self.connections_file = os.path.join(self.config_dir, "connections.yaml")
        
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Load saved connections
        self.load_connections()
    
    def load_connections(self):
        """Load saved connections from file."""
        if os.path.exists(self.connections_file):
            try:
                with open(self.connections_file, 'r') as f:
                    self.connections = yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading connections: {e}")
                self.connections = []
        else:
            self.connections = []
    
    def save_connections(self):
        """Save connections to file."""
        try:
            with open(self.connections_file, 'w') as f:
                yaml.dump(self.connections, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving connections: {e}")
    
    def get_all_connections(self):
        """Return all saved connections."""
        return self.connections
    
    def get_connection(self, name):
        """Get a connection by name."""
        for conn in self.connections:
            if conn["name"] == name:
                return conn
        return None
    
    def add_connection(self, connection):
        """Add a new connection."""
        # Check if connection with same name already exists
        existing = self.get_connection(connection["name"])
        if existing:
            # Update existing connection
            for i, conn in enumerate(self.connections):
                if conn["name"] == connection["name"]:
                    self.connections[i] = connection
                    break
        else:
            # Add new connection
            self.connections.append(connection)
        
        # Save to file
        self.save_connections()
    
    def remove_connection(self, name):
        """Remove a connection by name."""
        self.connections = [conn for conn in self.connections if conn["name"] != name]
        self.save_connections()
    
    def import_from_file(self, file_path):
        """Import connections from file."""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    imported = json.load(f)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                with open(file_path, 'r') as f:
                    imported = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format")
            
            # Merge with existing connections
            for conn in imported:
                self.add_connection(conn)
            
            return True
        except Exception as e:
            print(f"Error importing connections: {e}")
            return False
    
    def export_to_file(self, file_path):
        """Export connections to file."""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump(self.connections, f, indent=4)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                with open(file_path, 'w') as f:
                    yaml.dump(self.connections, f, default_flow_style=False)
            else:
                raise ValueError("Unsupported file format")
            
            return True
        except Exception as e:
            print(f"Error exporting connections: {e}")
            return False
