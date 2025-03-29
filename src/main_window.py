#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                            QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QLineEdit,
                            QGroupBox, QFormLayout, QSpinBox, QTextEdit, QTabWidget,
                            QMenu, QMessageBox, QDialog, QDialogButtonBox, QInputDialog,
                            QAction)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFont

from .ssh_terminal import SSHTerminal
from .connection_manager import ConnectionManager
from .custom_commands import CustomCommandsManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window properties
        self.setWindowTitle("SSHWorks Client")
        self.setMinimumSize(1024, 768)
        
        # Initialize managers
        self.connection_manager = ConnectionManager()
        self.custom_commands_manager = CustomCommandsManager()
        
        # Setup UI
        self.setup_ui()
        
        # Load saved connections
        self.load_saved_connections()
    
    def setup_ui(self):
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        
        # Left panel for connections and custom commands
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # Connections group
        self.connections_group = QGroupBox("Saved Connections")
        self.connections_layout = QVBoxLayout()
        
        # Connections tree
        self.connections_tree = QTreeWidget()
        self.connections_tree.setHeaderLabels(["Name"])
        self.connections_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connections_tree.customContextMenuRequested.connect(self.show_connection_context_menu)
        self.connections_tree.itemDoubleClicked.connect(self.connect_to_saved)
        
        # Connections buttons
        self.connections_buttons_layout = QHBoxLayout()
        self.add_connection_btn = QPushButton("Add")
        self.add_connection_btn.clicked.connect(self.add_connection_dialog)
        self.edit_connection_btn = QPushButton("Edit")
        self.edit_connection_btn.clicked.connect(self.edit_connection)
        self.remove_connection_btn = QPushButton("Remove")
        self.remove_connection_btn.clicked.connect(self.remove_connection)
        
        self.connections_buttons_layout.addWidget(self.add_connection_btn)
        self.connections_buttons_layout.addWidget(self.edit_connection_btn)
        self.connections_buttons_layout.addWidget(self.remove_connection_btn)
        
        self.connections_layout.addWidget(self.connections_tree)
        self.connections_layout.addLayout(self.connections_buttons_layout)
        self.connections_group.setLayout(self.connections_layout)
        
        # Custom commands group
        self.commands_group = QGroupBox("Custom Commands")
        self.commands_layout = QVBoxLayout()
        
        # Commands tree
        self.commands_tree = QTreeWidget()
        self.commands_tree.setHeaderLabels(["Name", "Command"])
        self.commands_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.commands_tree.customContextMenuRequested.connect(self.show_command_context_menu)
        self.commands_tree.itemDoubleClicked.connect(self.execute_custom_command)
        
        # Commands buttons
        self.commands_buttons_layout = QHBoxLayout()
        self.add_command_btn = QPushButton("Add")
        self.add_command_btn.clicked.connect(self.add_command_dialog)
        self.edit_command_btn = QPushButton("Edit")
        self.edit_command_btn.clicked.connect(self.edit_command)
        self.remove_command_btn = QPushButton("Remove")
        self.remove_command_btn.clicked.connect(self.remove_command)
        
        self.commands_buttons_layout.addWidget(self.add_command_btn)
        self.commands_buttons_layout.addWidget(self.edit_command_btn)
        self.commands_buttons_layout.addWidget(self.remove_command_btn)
        
        self.commands_layout.addWidget(self.commands_tree)
        self.commands_layout.addLayout(self.commands_buttons_layout)
        self.commands_group.setLayout(self.commands_layout)
        
        # Add connection and command groups to left panel
        self.left_layout.addWidget(self.connections_group)
        self.left_layout.addWidget(self.commands_group)
        
        # Right panel for connection details and terminal tabs
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # Quick connect form
        self.quick_connect_group = QGroupBox("Quick Connect")
        self.quick_connect_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.quick_connect_layout.addRow("Host:", self.host_input)
        self.quick_connect_layout.addRow("Port:", self.port_input)
        self.quick_connect_layout.addRow("Username:", self.username_input)
        self.quick_connect_layout.addRow("Password:", self.password_input)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.quick_connect)
        self.quick_connect_layout.addRow("", self.connect_button)
        
        self.quick_connect_group.setLayout(self.quick_connect_layout)
        
        # Terminal tabs
        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setTabsClosable(True)
        self.terminal_tabs.tabCloseRequested.connect(self.close_terminal_tab)
        
        # Add components to right panel
        self.right_layout.addWidget(self.quick_connect_group)
        self.right_layout.addWidget(self.terminal_tabs)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
        
        # Setup menu bar
        self.setup_menu_bar()
    
    def setup_menu_bar(self):
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_connection_action = QAction("New Connection", self)
        new_connection_action.triggered.connect(self.add_connection_dialog)
        file_menu.addAction(new_connection_action)
        
        import_action = QAction("Import Connections", self)
        import_action.triggered.connect(self.import_connections)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export Connections", self)
        export_action.triggered.connect(self.export_connections)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)
        
        # Connection menu
        conn_menu = self.menuBar().addMenu("&Connection")
        
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.quick_connect)
        conn_menu.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect_current)
        conn_menu.addAction(disconnect_action)
        
        conn_menu.addSeparator()
        
        manage_action = QAction("Manage Connections", self)
        manage_action.triggered.connect(self.manage_connections)
        conn_menu.addAction(manage_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    # ===== Connection Management =====
    def load_saved_connections(self):
        connections = self.connection_manager.get_all_connections()
        self.connections_tree.clear()
        
        for conn in connections:
            item = QTreeWidgetItem(self.connections_tree)
            item.setText(0, conn["name"])
            item.setData(0, Qt.UserRole, conn)
    
    def add_connection_dialog(self):
        # This would be a more detailed dialog in a real implementation
        name, ok = QInputDialog.getText(self, "New Connection", "Connection Name:")
        if not ok or not name:
            return
            
        host, ok = QInputDialog.getText(self, "New Connection", "Host:")
        if not ok or not host:
            return
            
        port, ok = QInputDialog.getInt(self, "New Connection", "Port:", 22, 1, 65535)
        if not ok:
            return
            
        username, ok = QInputDialog.getText(self, "New Connection", "Username:")
        if not ok:
            return
            
        password, ok = QInputDialog.getText(self, "New Connection", "Password:", 
                                            QLineEdit.Password)
        if not ok:
            return
        
        connection = {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password  # In real app, this should be encrypted
        }
        
        self.connection_manager.add_connection(connection)
        self.load_saved_connections()
    
    def edit_connection(self):
        selected = self.connections_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "No connection selected.")
            return
            
        # In a real implementation, this would populate a dialog with existing values
        connection = selected.data(0, Qt.UserRole)
        # For simplicity, just update the connection with the same dialog
        self.add_connection_dialog()
    
    def remove_connection(self):
        selected = self.connections_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "No connection selected.")
            return
            
        connection = selected.data(0, Qt.UserRole)
        
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the connection '{connection['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.connection_manager.remove_connection(connection["name"])
            self.load_saved_connections()
    
    def show_connection_context_menu(self, position):
        menu = QMenu()
        connect_action = menu.addAction("Connect")
        edit_action = menu.addAction("Edit")
        remove_action = menu.addAction("Remove")
        
        selected_action = menu.exec(self.connections_tree.mapToGlobal(position))
        
        if selected_action == connect_action:
            self.connect_to_saved()
        elif selected_action == edit_action:
            self.edit_connection()
        elif selected_action == remove_action:
            self.remove_connection()
    
    def connect_to_saved(self):
        selected = self.connections_tree.currentItem()
        if not selected:
            return
            
        connection = selected.data(0, Qt.UserRole)
        self.create_terminal_tab(connection)
    
    def quick_connect(self):
        connection = {
            "name": f"{self.username_input.text()}@{self.host_input.text()}",
            "host": self.host_input.text(),
            "port": self.port_input.value(),
            "username": self.username_input.text(),
            "password": self.password_input.text()
        }
        
        if not connection["host"]:
            QMessageBox.warning(self, "Warning", "Host is required.")
            return
            
        if not connection["username"]:
            QMessageBox.warning(self, "Warning", "Username is required.")
            return
        
        self.create_terminal_tab(connection)
    
    def create_terminal_tab(self, connection):
        # Create a new SSH terminal
        terminal = SSHTerminal(connection)
        
        # Connect signals
        terminal.connection_established.connect(
            lambda: self.connection_success(terminal, connection))
        terminal.connection_failed.connect(
            lambda error: self.connection_failed(error, connection))
        
        # Add a loading tab
        index = self.terminal_tabs.addTab(QWidget(), f"Connecting to {connection['name']}...")
        self.terminal_tabs.setCurrentIndex(index)
        
        # Start connection
        terminal.connect_to_host()
    
    def connection_success(self, terminal, connection):
        # Find the loading tab and replace it
        for i in range(self.terminal_tabs.count()):
            if self.terminal_tabs.tabText(i).startswith(f"Connecting to {connection['name']}"):
                self.terminal_tabs.removeTab(i)
                break
        
        # Add the successful connection tab
        index = self.terminal_tabs.addTab(terminal, connection['name'])
        self.terminal_tabs.setCurrentIndex(index)
        
        # Enable custom commands for this terminal
        terminal.set_custom_commands(self.custom_commands_manager.get_all_commands())
    
    def connection_failed(self, error, connection):
        # Find the loading tab and remove it
        for i in range(self.terminal_tabs.count()):
            if self.terminal_tabs.tabText(i).startswith(f"Connecting to {connection['name']}"):
                self.terminal_tabs.removeTab(i)
                break
        
        QMessageBox.critical(self, "Connection Failed", 
                            f"Failed to connect to {connection['name']}: {error}")
    
    def close_terminal_tab(self, index):
        terminal = self.terminal_tabs.widget(index)
        if isinstance(terminal, SSHTerminal):
            terminal.disconnect_from_host()
        self.terminal_tabs.removeTab(index)
    
    def disconnect_current(self):
        current_index = self.terminal_tabs.currentIndex()
        if current_index >= 0:
            self.close_terminal_tab(current_index)
    
    # ===== Custom Commands =====
    def load_custom_commands(self):
        commands = self.custom_commands_manager.get_all_commands()
        self.commands_tree.clear()
        
        for cmd in commands:
            item = QTreeWidgetItem(self.commands_tree)
            item.setText(0, cmd["name"])
            item.setText(1, cmd["command"])
            item.setData(0, Qt.UserRole, cmd)
    
    def add_command_dialog(self):
        name, ok = QInputDialog.getText(self, "New Command", "Command Name:")
        if not ok or not name:
            return
            
        command, ok = QInputDialog.getText(self, "New Command", "Command:")
        if not ok or not command:
            return
        
        cmd = {
            "name": name,
            "command": command
        }
        
        self.custom_commands_manager.add_command(cmd)
        self.load_custom_commands()
    
    def edit_command(self):
        selected = self.commands_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "No command selected.")
            return
            
        # In a real implementation, this would populate a dialog with existing values
        cmd = selected.data(0, Qt.UserRole)
        # For simplicity, just update the command with the same dialog
        self.add_command_dialog()
    
    def remove_command(self):
        selected = self.commands_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Warning", "No command selected.")
            return
            
        cmd = selected.data(0, Qt.UserRole)
        
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete the command '{cmd['name']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.custom_commands_manager.remove_command(cmd["name"])
            self.load_custom_commands()
    
    def show_command_context_menu(self, position):
        menu = QMenu()
        execute_action = menu.addAction("Execute")
        edit_action = menu.addAction("Edit")
        remove_action = menu.addAction("Remove")
        
        selected_action = menu.exec(self.commands_tree.mapToGlobal(position))
        
        if selected_action == execute_action:
            self.execute_custom_command()
        elif selected_action == edit_action:
            self.edit_command()
        elif selected_action == remove_action:
            self.remove_command()
    
    def execute_custom_command(self):
        selected = self.commands_tree.currentItem()
        if not selected:
            return
            
        cmd = selected.data(0, Qt.UserRole)
        
        current_tab = self.terminal_tabs.currentWidget()
        if not isinstance(current_tab, SSHTerminal):
            QMessageBox.warning(self, "Warning", "No active terminal to execute command.")
            return
            
        current_tab.execute_command(cmd["command"])
    
    # ===== Other Functions =====
    def import_connections(self):
        # In a real app, this would show a file dialog and import from a file
        QMessageBox.information(self, "Info", "Import connections feature not implemented yet.")
    
    def export_connections(self):
        # In a real app, this would show a file dialog and export to a file
        QMessageBox.information(self, "Info", "Export connections feature not implemented yet.")
    
    def show_preferences(self):
        QMessageBox.information(self, "Info", "Preferences dialog not implemented yet.")
    
    def manage_connections(self):
        # In a real app, this would show a comprehensive connection manager dialog
        QMessageBox.information(self, "Info", "Connection manager not implemented yet.")
    
    def show_about(self):
        QMessageBox.about(
            self, 
            "About SSHWorks Client",
            """
            <h1>SSHWorks Client</h1>
            <p>Version 1.0.0</p>
            <p>A feature-rich SSH client with a modern GUI.</p>
            <p>&copy; 2025 SSHWorks</p>
            """
        )
