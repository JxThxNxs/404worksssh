#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QHBoxLayout, QPushButton, QMenu, QAction, QAction
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QTimer
from PyQt5.QtGui import QTextCursor, QColor, QFont, QTextCharFormat

import paramiko
import time
import socket
import threading
import re

class SSHWorker(QThread):
    output_received = pyqtSignal(str)
    connection_established = pyqtSignal()
    connection_failed = pyqtSignal(str)
    connection_closed = pyqtSignal()
    
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.channel = None
        self.running = False
        self.command_queue = []
        self.lock = threading.Lock()
    
    def run(self):
        try:
            # Connect to the SSH server
            self.client.connect(
                hostname=self.connection['host'],
                port=self.connection['port'],
                username=self.connection['username'],
                password=self.connection['password'],
                timeout=10
            )
            
            # Open channel and invoke shell
            self.channel = self.client.invoke_shell()
            self.channel.settimeout(0.1)
            
            # Signal connection established
            self.connection_established.emit()
            
            # Main loop to read from channel
            self.running = True
            buffer = ""
            
            while self.running:
                # Process any queued commands
                with self.lock:
                    if self.command_queue:
                        command = self.command_queue.pop(0)
                        self.channel.send(command)
                
                # Read from channel
                try:
                    if self.channel.recv_ready():
                        chunk = self.channel.recv(1024).decode('utf-8', errors='replace')
                        buffer += chunk
                        self.output_received.emit(chunk)
                except socket.timeout:
                    pass
                except Exception as e:
                    if self.running:  # Only emit error if we're still supposed to be running
                        self.connection_failed.emit(str(e))
                        self.running = False
                
                # Short sleep to prevent CPU hogging
                time.sleep(0.01)
            
        except Exception as e:
            self.connection_failed.emit(str(e))
        finally:
            if self.channel:
                self.channel.close()
            self.client.close()
            self.connection_closed.emit()
    
    def stop(self):
        self.running = False
        self.wait()
    
    def send_command(self, command):
        with self.lock:
            self.command_queue.append(command + "\n")

class SSHTerminal(QWidget):
    connection_established = pyqtSignal()
    connection_failed = pyqtSignal(str)
    
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.ssh_worker = None
        self.custom_commands = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Terminal output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setLineWrapMode(QTextEdit.WidgetWidth)
        self.terminal_output.setFont(QFont("Courier New", 10))
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
            }
        """)
        
        # Input area
        self.input_widget = QWidget()
        self.input_layout = QHBoxLayout(self.input_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.command_input = QLineEdit()
        self.command_input.setFont(QFont("Courier New", 10))
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                border-top: 1px solid #444444;
                padding: 5px;
            }
        """)
        self.command_input.returnPressed.connect(self.send_command)
        
        self.custom_cmd_button = QPushButton("▼")
        self.custom_cmd_button.setFixedWidth(25)
        self.custom_cmd_button.clicked.connect(self.show_custom_commands_menu)
        
        self.input_layout.addWidget(self.command_input)
        self.input_layout.addWidget(self.custom_cmd_button)
        
        # Add to main layout
        self.layout.addWidget(self.terminal_output)
        self.layout.addWidget(self.input_widget)
    
    def connect_to_host(self):
        # Display connecting message
        self.append_output(f"Connecting to {self.connection['host']}:{self.connection['port']} as {self.connection['username']}...\n")
        
        # Create and start worker thread
        self.ssh_worker = SSHWorker(self.connection)
        self.ssh_worker.output_received.connect(self.append_output)
        self.ssh_worker.connection_established.connect(self.on_connected)
        self.ssh_worker.connection_failed.connect(self.on_connection_failed)
        self.ssh_worker.connection_closed.connect(self.on_connection_closed)
        self.ssh_worker.start()
    
    def disconnect_from_host(self):
        if self.ssh_worker and self.ssh_worker.running:
            self.append_output("\nDisconnecting...\n")
            self.ssh_worker.stop()
    
    def on_connected(self):
        self.append_output("Connection established.\n")
        self.command_input.setFocus()
        self.connection_established.emit()
    
    def on_connection_failed(self, error):
        self.append_output(f"Connection failed: {error}\n")
        self.connection_failed.emit(error)
    
    def on_connection_closed(self):
        self.append_output("Connection closed.\n")
    
    def send_command(self):
        command = self.command_input.text()
        if command and self.ssh_worker and self.ssh_worker.running:
            self.ssh_worker.send_command(command)
            self.command_input.clear()
    
    def execute_command(self, command):
        if self.ssh_worker and self.ssh_worker.running:
            self.ssh_worker.send_command(command)
            self.append_output(f"\n$ {command}\n")
    
    def append_output(self, text):
        cursor = self.terminal_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Simple ANSI color handling (very basic implementation)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        plain_text = ansi_escape.sub('', text)
        
        # Insert the text
        cursor.insertText(plain_text)
        
        # Scroll to the bottom
        cursor.movePosition(QTextCursor.End)
        self.terminal_output.setTextCursor(cursor)
    
    def set_custom_commands(self, commands):
        self.custom_commands = commands
    
    def show_custom_commands_menu(self):
        menu = QMenu(self)
        
        if not self.custom_commands:
            action = QAction("No custom commands defined", self)
            action.setEnabled(False)
            menu.addAction(action)
        else:
            for cmd in self.custom_commands:
                action = QAction(cmd["name"], self)
                action.setData(cmd["command"])
                action.triggered.connect(lambda checked, cmd=cmd: self.execute_command(cmd["command"]))
                menu.addAction(action)
        
        menu.exec(self.custom_cmd_button.mapToGlobal(self.custom_cmd_button.rect().bottomLeft()))
