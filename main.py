#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from src.splash_screen import SplashScreen
from src.main_window import MainWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Create main window but don't show yet
    main_window = MainWindow()
    
    # Timer to simulate loading and then show main window
    def finish_splash():
        splash.close()
        main_window.show()
    
    # Connect splash screen finished signal
    splash.animation_finished.connect(finish_splash)
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    # Ensure src directory is in path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
