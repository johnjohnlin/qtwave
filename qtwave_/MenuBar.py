from PyQt6.QtWidgets import (
	QMenu,
)
from PyQt6.QtGui import (
	QAction,
)

class MenuBar:
	def __init__(self, main_window):
		self.main_window = main_window

		# Create the menu bar
		menu_bar = self.main_window.menuBar()

		# Create the File menu
		self.file_menu = QMenu("File", self.main_window)
		menu_bar.addMenu(self.file_menu)

		# Create actions for the File menu
		self.exit_action = QAction("Exit", self.main_window)
		self.exit_action.triggered.connect(self.main_window.close)
		self.file_menu.addAction(self.exit_action)

		# Create the Help menu (similar to File menu)
		self.help_menu = QMenu("Help", self.main_window)
		menu_bar.addMenu(self.help_menu)

		self.about_action = QAction("About", self.main_window)
		self.about_action.triggered.connect(lambda: self.show_message("This is a menu bar example"))
		self.help_menu.addAction(self.about_action)

	def show_message(self, message):
		# Display a message box (can be replaced with your custom functionality)
		from PyQt6.QtWidgets import QMessageBox
		QMessageBox.information(self.main_window, "About", message)
