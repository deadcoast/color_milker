import csv
import functools
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime

from PyQt6.QtCore import QObject, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QGuiApplication, QIcon, QImage, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


# --- Palette Window ---
class PaletteWindow(QWidget):
    """A separate window to display saved colors."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Palette")
        self.setMinimumWidth(200)
        self.setMinimumHeight(300) # Start with a decent size
        self.colors = [] # Store QColor objects

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # Scroll Area for colors
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Colors stack from top
        self.scroll_layout.setSpacing(4)

        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Add button panel for various operations
        self.button_panel = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_palette)
        self.button_panel.addWidget(self.clear_button)
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.show_export_menu)
        self.export_button.setToolTip("Export palette to file")
        self.button_panel.addWidget(self.export_button)
        
        # Add button panel to main layout
        self.main_layout.addLayout(self.button_panel)
        
        # Create export menu
        self.export_menu = QMenu(self)
        self.export_json_action = QAction("Export as JSON", self)
        self.export_json_action.triggered.connect(self.export_as_json)
        self.export_csv_action = QAction("Export as CSV", self)
        self.export_csv_action.triggered.connect(self.export_as_csv)
        self.export_menu.addAction(self.export_json_action)
        self.export_menu.addAction(self.export_csv_action)

    def show_export_menu(self):
        """Shows the export menu dropdown."""
        if not self.colors:
            QMessageBox.warning(self, "Empty Palette", "Cannot export an empty palette.")
            return
            
        # Position the menu under the export button
        self.export_menu.exec(self.export_button.mapToGlobal(self.export_button.rect().bottomLeft()))

    def export_as_json(self):
        """Export palette as JSON file."""
        if not self.colors:
            return
            
        # Create default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"color_palette_{timestamp}.json"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Palette as JSON", default_filename, "JSON Files (*.json)"
        )
        
        if not filename:
            return  # User cancelled
            
        # Convert colors to hex values
        color_data = [{"hex": color.name().upper(), "rgb": [color.red(), color.green(), color.blue()]} 
                      for color in self.colors]
        
        try:
            with open(filename, 'w') as f:
                json.dump({"colors": color_data}, f, indent=2)
            
            self._show_export_success_message(filename)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export palette: {str(e)}")
    
    def export_as_csv(self):
        """Export palette as CSV file."""
        if not self.colors:
            return
            
        # Create default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"color_palette_{timestamp}.csv"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Palette as CSV", default_filename, "CSV Files (*.csv)"
        )
        
        if not filename:
            return  # User cancelled
            
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["HEX", "R", "G", "B"])
                # Write color data
                for color in self.colors:
                    writer.writerow([
                        color.name().upper(),
                        color.red(),
                        color.green(),
                        color.blue()
                    ])
            
            self._show_export_success_message(filename)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export palette: {str(e)}")
    
    def _show_export_success_message(self, filepath):
        """Show success message after export."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Export Successful")
        msg.setText("Palette exported successfully!")
        msg.setInformativeText(f"File saved to:\n{filepath}")
        msg.exec()

    def add_color(self, color: QColor):
        """Adds a color swatch and hex label to the palette."""
        if not isinstance(color, QColor) or not color.isValid():
            print("Invalid color passed to palette")
            return

        hex_code = color.name().upper() # Get #RRGGBB format

        # Avoid adding duplicates immediately after each other (optional)
        # if self.colors and self.colors[-1] == color:
        #     return 

        self.colors.append(color)

        # Create display widget for this color
        color_widget = QWidget()
        color_widget.setMinimumHeight(25) # Make swatches decent height
        color_widget.setAutoFillBackground(True)
        palette = color_widget.palette()
        palette.setColor(color_widget.backgroundRole(), color)
        color_widget.setPalette(palette)
        # Add tooltip for the color name
        color_widget.setToolTip(f"Click to copy {hex_code}")
        
        # --- Make the color widget clickable to copy hex ---
        # Define a nested function taking hex_code first
        def on_color_widget_click(h: str, event: QMouseEvent | None) -> None:
            # Check if event is not None and is a left click
            if event and event.button() == Qt.MouseButton.LeftButton:
                self.copy_to_clipboard(h)
        
        # Use functools.partial to create the event handler
        color_widget.mousePressEvent = functools.partial(on_color_widget_click, hex_code) #type: ignore
        # --- End clickable widget section ---


        hex_label = QLabel(hex_code)
        hex_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hex_label.setToolTip(f"Click color swatch to copy {hex_code}")

        entry_layout = QHBoxLayout()
        entry_layout.addWidget(color_widget, 1) # Color takes more space
        entry_layout.addWidget(hex_label, 1) # Label takes space too
        entry_layout.setSpacing(10)
        
        # Add the HBox layout to the main VBox layout inside scroll area
        self.scroll_layout.addLayout(entry_layout)
        
        # Scroll to bottom (optional, shows newest color)
        QApplication.processEvents() # Ensure layout is updated before scrolling
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())


    def copy_to_clipboard(self, text):
        """Copies the provided text to the system clipboard."""
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            print(f"Copied to clipboard: {text}")
            # Optional: Show temporary status message
            parent_widget = self.parent()
            # Check type first, then get and check status bar
            if isinstance(parent_widget, QMainWindow):
                 status_bar = parent_widget.statusBar()
                 if status_bar: # Check if statusBar() returned a valid object
                     status_bar.showMessage(f"Copied: {text}", 2000) # Show for 2 seconds
        else:
            print("Error: Could not access clipboard.")


    def clear_palette(self):
        """Removes all colors from the palette display."""
        if not self.colors:
            return
            
        # Ask for confirmation only if there are colors
        if self.colors:
            reply = QMessageBox.question(
                self, "Clear Palette", 
                "Are you sure you want to clear the entire palette?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        self.colors = []
        # Remove widgets from layout safely
        while self.scroll_layout.count():
            layout_item = self.scroll_layout.takeAt(0)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    # Check if it's a layout
                    sub_layout = layout_item.layout()
                    if sub_layout is not None:
                        # Clear widgets within the sub-layout (QHBoxLayout)
                        while sub_layout.count():
                            sub_item = sub_layout.takeAt(0)
                            if sub_item is not None:
                                sub_widget = sub_item.widget()
                                if sub_widget is not None:
                                    sub_widget.deleteLater()
                        # After clearing items, we might want to delete the layout itself,
                        # but taking it from the parent layout usually handles this.

# --- Color Grabber Logic ---
class ScreenColorGrabber(QObject):
    """Handles the screen grabbing process using macOS's screenshot capability."""
    color_grabbed = pyqtSignal(QColor) # Signal emitted when color is selected
    grabbing_finished = pyqtSignal() # Signal emitted when grabbing stops

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_grabbing = False
        self._temp_file = None

    def start_grabbing(self):
        """Initiates the color grabbing process using screencapture."""
        if self._is_grabbing:
            return
        self._is_grabbing = True
        
        # Create a temporary file for the screenshot
        fd, self._temp_file = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        
        try:
            # Use macOS screencapture tool with interactive mode
            # This lets the user select a portion of the screen
            print(f"Taking screenshot to {self._temp_file}")
            subprocess.run(['screencapture', '-i', '-o', '-t', 'png', self._temp_file], check=True)
            
            # Check if the file exists and has content (user didn't cancel)
            if os.path.exists(self._temp_file) and os.path.getsize(self._temp_file) > 0:
                # Load the image and grab the center pixel
                self._get_color_from_screenshot()
            else:
                print("Screenshot was cancelled")
                self._cancel_grabbing("Screenshot cancelled")
        except subprocess.SubprocessError as e:
            self._cancel_grabbing(f"Error capturing screenshot: {e}")
        
        # Clean up
        self.stop_grabbing()

    def _get_color_from_screenshot(self):
        """Extract the color from the center of the screenshot."""
        if not self._temp_file or not os.path.exists(self._temp_file):
            return
            
        # Load the image using QImage
        image = QImage(self._temp_file)
        
        if image.isNull():
            print("Failed to load screenshot image")
            return
            
        # Get color from center pixel
        width = image.width()
        height = image.height()
        
        if width <= 0 or height <= 0:
            print("Invalid image dimensions")
            return
            
        # Get the center pixel
        center_x = width // 2
        center_y = height // 2
        center_color = QColor(image.pixel(center_x, center_y))
        
        if center_color.isValid():
            print(f"Grabbed color: {center_color.name().upper()}")
            self.color_grabbed.emit(center_color)
        else:
            print("Invalid color grabbed")

    def stop_grabbing(self):
        """Stops the color grabbing mode."""
        if not self._is_grabbing:
            return
            
        self._is_grabbing = False
        
        # Clean up temp file
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.unlink(self._temp_file)
            except OSError as e:
                print(f"Error removing temp file: {e}")
            self._temp_file = None
            
        self.grabbing_finished.emit()
        print("Grabbing mode finished.")

    def _cancel_grabbing(self, message):
        print(message)
        self.stop_grabbing()

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Color Grabber")
        self.current_color = QColor(Qt.GlobalColor.white) # Default color
        self.details_visible = True # Start expanded

        # --- Palette Window (create it early as a separate window) ---
        self.palette_window = PaletteWindow()  # No parent! Make it a separate window
        self.palette_window.setWindowTitle("Color Palette")
        
        # Get style object for icons, checking for None
        style = QApplication.style()
        default_icon = QIcon() # Empty icon as fallback

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.setCentralWidget(self.central_widget)

        # --- Top Bar Layout (Buttons) ---
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setSpacing(5)

        # Grab Button with Icon
        self.grab_button = QPushButton(" Grab Color")
        self.grab_button.setToolTip("Click then click anywhere on screen to grab color")
        grab_icon = style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp) if style else default_icon
        self.grab_button.setIcon(grab_icon)
        self.grab_button.setMinimumWidth(110)  # Ensure button is visible

        # Toggle Button with Icon only
        self.toggle_button = QPushButton() # No text
        self.toggle_button.setToolTip("Show/Hide color preview")
        self.toggle_button.setMinimumWidth(40)  # Ensure button is visible
        # Initial icon set in update_toggle_button_icon

        # Palette Menu Button
        self.palette_button = QToolButton()
        self.palette_button.setToolTip("Palette options")
        # Use SP_DialogSaveButton for the palette icon
        palette_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton) if style else default_icon
        self.palette_button.setIcon(palette_icon)
        self.palette_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.palette_button.setMinimumWidth(40)  # Ensure button is visible

        # Create Palette Menu
        self.palette_menu = QMenu(self)
        self.show_palette_action = QAction("Show Palette", self) # Text updated dynamically
        self.show_palette_action.triggered.connect(self.toggle_palette_visibility)
        self.add_action = QAction("Add Current to Palette", self)
        self.add_action.triggered.connect(self.add_current_color_to_palette)
        self.palette_menu.addAction(self.show_palette_action)
        self.palette_menu.addAction(self.add_action)
        self.palette_menu.aboutToShow.connect(self.update_palette_menu) # Update state before showing
        self.palette_button.setMenu(self.palette_menu)

        # Add buttons to layout
        self.top_bar_layout.addWidget(self.grab_button)
        self.top_bar_layout.addWidget(self.toggle_button)
        self.top_bar_layout.addWidget(self.palette_button) # Palette button on the right

        self.main_layout.addLayout(self.top_bar_layout)

        # --- Details Container (Color Preview, Hex) --- REMOVED Add Button
        self.details_container = QWidget()
        self.details_layout = QHBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(0, 5, 0, 0)
        self.details_layout.setSpacing(10)

        # Color Preview Widget
        self.color_display = QFrame()
        self.color_display.setFrameShape(QFrame.Shape.StyledPanel)
        self.color_display.setFixedSize(QSize(50, 50))
        self.color_display.setAutoFillBackground(True)

        # Hex Label
        self.hex_label = QLabel("Hex: #FFFFFF")
        self.hex_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.hex_label.setToolTip("Hexadecimal value of the selected color")

        self.details_layout.addWidget(self.color_display)
        self.details_layout.addWidget(self.hex_label, 1)

        self.main_layout.addWidget(self.details_container)

        # --- Adjust Size --- (Set explicit minimum sizes)
        self.update_color_display(self.current_color)
        self.central_widget.adjustSize()
        self.resize(self.central_widget.sizeHint()) # Resize to hint
        self.setMinimumWidth(350)  # Larger minimum width to fit all buttons properly

        # --- Color Grabber Instance ---
        self.color_grabber = ScreenColorGrabber(self)

        # --- Status Bar ---
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Ready", 3000)

        # --- Connect Signals ---
        self.grab_button.clicked.connect(self.start_color_grab)
        self.toggle_button.clicked.connect(self.toggle_details_visibility)
        self.color_grabber.color_grabbed.connect(self.update_color_display)
        self.color_grabber.grabbing_finished.connect(self.on_grabbing_finished)

        # Initialize toggle state (sets icon)
        self.update_toggle_button_icon() # Renamed call

    # --- Methods ---

    def start_color_grab(self):
        """Initiates the screen grabbing process."""
        print("Starting color grab from main window...")
        self.grab_button.setEnabled(False)
        
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage("Select an area on screen to grab the color from its center...", 0)
        
        # Make the button show we're in grabbing mode
        self.grab_button.setText("Grabbing...")
        
        # Start grabbing
        self.color_grabber.start_grabbing()

    def on_grabbing_finished(self):
        """Called when grabbing is done or cancelled."""
        print("Grabbing finished...")
        self.grab_button.setEnabled(True)
        
        # Reset button text
        self.grab_button.setText(" Grab Color")
        
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.clearMessage()
            if self.current_color.isValid():
                 status_bar.showMessage(f"Grabbed: {self.current_color.name().upper()}", 3000)
            else:
                 status_bar.showMessage("Grabbing cancelled or failed.", 3000)

    def update_color_display(self, color: QColor):
        """Updates the color preview and hex label."""
        if not isinstance(color, QColor) or not color.isValid():
            print(f"Attempted to update display with invalid color: {color}")
            return

        self.current_color = color
        hex_code = color.name().upper()

        palette = self.color_display.palette()
        palette.setColor(self.color_display.backgroundRole(), color)
        self.color_display.setPalette(palette)
        self.color_display.setToolTip(f"Current color: {hex_code}\nUse palette button to add.") # Updated tooltip

        self.hex_label.setText(f"Hex: {hex_code}")

    def toggle_details_visibility(self):
        """Shows or hides the color preview and hex label section."""
        self.details_visible = not self.details_visible
        self.details_container.setVisible(self.details_visible)
        self.update_toggle_button_icon() # Update icon after toggle
        # Adjust window height dynamically
        self.resize(self.width(), self.central_widget.sizeHint().height())

    # Renamed method to update icon
    def update_toggle_button_icon(self):
         style = QApplication.style()
         default_icon = QIcon()
         if self.details_visible:
             icon = style.standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton) if style else default_icon # Icon to collapse
             self.toggle_button.setToolTip("Collapse color preview")
         else:
             icon = style.standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton) if style else default_icon # Icon to expand
             self.toggle_button.setToolTip("Expand color preview")
         self.toggle_button.setIcon(icon)

    # New method to handle toggling palette window from action
    def toggle_palette_visibility(self):
        if self.palette_window.isVisible():
            self.palette_window.hide()
            # Update the menu item text immediately
            self.show_palette_action.setText("Show Palette")
        else:
            # Show the palette window
            self.show_palette()
            # Update the menu item text immediately
            self.show_palette_action.setText("Hide Palette")
            
        # Force update the UI
        QApplication.processEvents()

    # Renamed original show_palette, now just ensures it's visible and positioned
    def show_palette(self):
        """Shows the palette window, positioning if hidden."""
        if self.palette_window.isHidden():
            main_pos = self.pos()
            main_size = self.size()
            # Place it to the right of the main window instead of below
            self.palette_window.move(main_pos.x() + main_size.width() + 10, main_pos.y())
            self.palette_window.show()
        else:
            self.palette_window.raise_()
            self.palette_window.activateWindow()

    # New method to update menu items just before showing
    def update_palette_menu(self):
        if self.palette_window.isVisible():
            self.show_palette_action.setText("Hide Palette")
        else:
            self.show_palette_action.setText("Show Palette")
        # Disable add action if no valid color is selected
        self.add_action.setEnabled(self.current_color.isValid())

    def add_current_color_to_palette(self):
        """Adds the currently displayed color to the palette window."""
        if self.current_color and self.current_color.isValid():
            self.palette_window.add_color(self.current_color)
            # Show palette if hidden when adding first color? (Optional)
            # if self.palette_window.isHidden() and len(self.palette_window.colors) == 1:
            #    self.show_palette() # Maybe too intrusive, let user open manually
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Added {self.current_color.name().upper()} to palette", 2000)
        else:
             status_bar = self.statusBar()
             if status_bar:
                 status_bar.showMessage("No valid color selected to add.", 2000)

    def closeEvent(self, event):
        """Ensure palette window also closes when main window closes."""
        if self.palette_window and self.palette_window.isVisible():
            self.palette_window.close()
        super().closeEvent(event)


# --- Application Entry Point ---
if __name__ == "__main__":
    # Use QGuiApplication for screen/clipboard access if QApplication not needed for widgets?
    # No, QApplication is needed for widgets.
    app = QApplication(sys.argv)
    # You can set an application icon here if you have one
    # app.setWindowIcon(QIcon('path/to/your/icon.png'))

    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())