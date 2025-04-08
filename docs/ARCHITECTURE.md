# SYSTEM ARCHITECTURE

## Core Functionality

- Main Window (Bar): A narrow main window.
- Expand/Collapse: A button to show/hide the color preview and hex code.
- Color Grabber: A button initiates grabbing mode. Clicking anywhere on the screen captures the color under the cursor.
- Color Display: Shows the grabbed color.
- Hex Display: Shows the hex code of the grabbed color.
- Palette Window: A separate window to store colors.
- Add to Palette: A button to save the currently displayed color to the palette.

## How it Works

### MainWindow:

- Sets up the main UI with buttons (Grab Color, Collapse/Expand, Show Palette) in a top QHBoxLayout.
- Creates a details_container (QWidget) holding the color_display (QFrame), hex_label (QLabel), and add_palette_button (QPushButton) in another QHBoxLayout.
- The toggle_details_visibility method hides or shows this details_container and adjusts the main window's fixed height accordingly using setFixedSize and sizeHint().
- It creates instances of ScreenColorGrabber and PaletteWindow.
- Connects button clicks to the appropriate methods (start_color_grab, toggle_details_visibility, show_palette, add_current_color_to_palette).
- Connects signals from the ScreenColorGrabber (color_grabbed, grabbing_finished) to update the UI (update_color_display, on_grabbing_finished).

### ScreenColorGrabber:

- Inherits from QObject to use signals/slots.
- start_grabbing: Changes the cursor to a crosshair, installs an eventFilter on the entire application (QApplication.instance()) to catch mouse events globally, and disables the grab button.
- eventFilter: This is the core of screen-wide grabbing. It checks if grabbing is active and if a mouse button was pressed.
- If Left Button: It gets the primary screen, grabs a 1x1 QPixmap at the current QCursor.pos(), converts it to a QColor, emits the color_grabbed signal with the color, and calls stop_grabbing.
- If Right Button: It cancels grabbing by calling stop_grabbing.
- It returns True if it handled the event, preventing further processing.
- stop_grabbing: Restores the normal cursor, removes the event filter, enables the grab button, and emits grabbing_finished.

### PaletteWindow:

- A separate QWidget that acts as the palette.
- Uses a QVBoxLayout inside a QScrollArea so the list of colors can grow infinitely.
- add_color: Creates a horizontal layout (QHBoxLayout) containing a colored QWidget (using setAutoFillBackground and setPalette) and a QLabel for the hex code. This layout is added to the vertical layout within the scroll area. It also makes the color swatch clickable to copy the hex code.
- copy_to_clipboard: Utility function using QApplication.clipboard().
- clear_palette: Removes all color entry widgets safely.