from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
import threading
import subprocess
import os
from jarvis import main

class SizeAnimator(QObject):
    sizeChanged = pyqtSignal(QSize)

    def animate(self, size, delay=0):
        QTimer.singleShot(delay, lambda: self.sizeChanged.emit(size))

class JarvisUI(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Jarvis UI')
        self.setGeometry(80, 80, 400, 400)

        # Set window attributes for transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Microphone image (zoomed and larger)
        self.mic_label = QLabel(self)
        self.add_gif_to_label(self.mic_label,
                              "cbe227_fb70e39e9dd94e30bbe30c48b2367dd8~mv2.gif",
                              size=(720, 220), alignment=Qt.AlignCenter)  # Initial size and alignment
        self.mic_label.setAlignment(Qt.AlignCenter)
        self.mic_label.mousePressEvent = self.start_listening

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.mic_label, alignment=Qt.AlignCenter)

        # Add some margins and spacing
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.process = None
        self.is_listening = False
        self.size_animator = SizeAnimator()
        self.size_animator.sizeChanged.connect(self.mic_label.setFixedSize)

    def add_gif_to_label(self, label, gif_path, size=None, alignment=None):
        movie = QMovie(gif_path)
        label.setMovie(movie)
        self.movie = movie  # Save reference to the movie
        movie.start()

        if size:
            label.setFixedSize(*size)

        if alignment:
            label.setAlignment(alignment)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        label.setGraphicsEffect(shadow)

    def start_listening(self, event):
        # Run the main file in a separate thread
        if not self.is_listening:
            self.is_listening = True
            subprocess_thread = threading.Thread(target=self.run_main_file)
            subprocess_thread.start()

    def run_main_file(self):
        try:
            # Get the directory where ui.py is located
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Specify the path to main.py based on the current directory
            path_to_main_py = os.path.join(current_directory, r"C:\Users\chatu\OneDrive\Desktop\J.A.R.V.I.S\MAIN\main.py")

            command = ["python", path_to_main_py]
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=current_directory)

            # Capture and display the output
            output, _ = self.process.communicate()
            self.handle_output(output)

            # Reset listening flag
            self.is_listening = False

        except subprocess.CalledProcessError as e:
            # Handle subprocess errors
            print(f"Error: {str(e)}")

    def handle_output(self, output):
        if output.strip():
            # If main file is printing anything, make the gif size bigger and smaller
            self.size_animator.animate(QSize(900, 280))
            self.size_animator.animate(QSize(720, 220), delay=500)
        else:
            # If main file is not printing anything, keep the gif in a normal position
            self.size_animator.animate(QSize(720, 220))

def UI():
    app = QApplication([])

    jarvis_ui = JarvisUI()
    jarvis_ui.showFullScreen()

    app.exec_()

t1 = threading.Thread(target=main)
t2 = threading.Thread(target=UI)
t1.start()
t2.start()
t1.join()
t2.join()