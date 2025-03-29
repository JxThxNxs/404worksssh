#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont

class SplashScreen(QSplashScreen):
    # Signal emitted when the animation is finished
    animation_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(600, 400)
        
        # Create base pixmap for drawing
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.black)
        self.setPixmap(self.pixmap)
        
        # Setup progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(100, 340, 400, 20)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                background-color: black;
            }
            QProgressBar::chunk {
                background-color: white;
            }
        """)
        self.progress_bar.setValue(0)
        
        # Animation state
        self.current_animation_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # Update every 50ms
        
        # Center the splash screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
    
    def update_animation(self):
        self.current_animation_step += 1
        progress = min(100, self.current_animation_step * 2)
        self.progress_bar.setValue(progress)
        
        # Create a new painter each time to draw current state
        painter = QPainter(self.pixmap)
        painter.fillRect(0, 0, self.width(), self.height(), QColor(0, 0, 0))
        
        # Animation phases
        if self.current_animation_step < 20:
            # Phase 1: Show "404" in red
            painter.setFont(QFont("Arial", 72, QFont.Bold))
            painter.setPen(QColor(255, 0, 0))  # Red
            painter.drawText(self.rect(), Qt.AlignCenter, "404")
            
        elif self.current_animation_step < 35:
            # Phase 2: Transition
            painter.setFont(QFont("Arial", 72, QFont.Bold))
            painter.setPen(QColor(255, 0, 0))  # Red
            painter.drawText(self.rect(), Qt.AlignCenter, "404")
            
            # Fade in "Works"
            opacity = (self.current_animation_step - 20) / 15.0
            painter.setFont(QFont("Arial", 72, QFont.Bold))
            painter.setPen(QColor(255, 255, 255, int(255 * opacity)))  # White with fade
            painter.drawText(self.rect(), Qt.AlignCenter, "Works")
            
        else:
            # Phase 3: Show "Works" and "SSH" in white
            painter.setFont(QFont("Arial", 72, QFont.Bold))
            painter.setPen(QColor(255, 255, 255))  # White
            painter.drawText(self.rect().adjusted(0, -50, 0, -50), Qt.AlignCenter, "Works")
            
            painter.setFont(QFont("Arial", 36, QFont.Bold))
            painter.drawText(self.rect().adjusted(0, 50, 0, 50), Qt.AlignCenter, "SSH")
        
        painter.end()
        self.setPixmap(self.pixmap)
        
        # Animation finished
        if progress >= 100:
            self.timer.stop()
            self.animation_finished.emit()

# For testing purposes
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    
    # Close after 5 seconds
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec_())
