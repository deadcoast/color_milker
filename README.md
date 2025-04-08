# Color Milker

A simple utility for grabbing colors from anywhere on your screen and creating color palettes.

## Features

- Grab colors from anywhere on screen, click and drag with native screenshot tool
- Save colors to a palette
- Copy color hex codes to clipboard with a click
- Export palettes to JSON or CSV format
- Simple, clean interface
- Minimal dependencies

## Installation

### Prerequisites

- Python 3.6+
- PyQt6
- macOS (for the screenshot functionality)

### Option 1: Install as a system command

```bash
# Clone the repository
git clone [repository-url] color_milker
cd color_milker

# Install dependencies
make deps

# Install as a system command
sudo make install
```

After installation, you can run the app from anywhere with:

```bash
cmilker
```

### Option 2: Run directly from source

```bash
# Clone the repository
git clone [repository-url] color_milker
cd color_milker

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install PyQt6

# Run the application
python src/main.py
```

## Usage

1. Click "Grab Color" to enter color grabbing mode
2. When the screenshot tool appears, select any area of the screen
3. The color from the center of your selection will be grabbed
4. To save to palette, click the palette icon and select "Add Current to Palette"
5. Export your palette using the "Export" button in the palette window

## Uninstallation

To remove the system command:

```bash
sudo make uninstall
```

## License

MIT 