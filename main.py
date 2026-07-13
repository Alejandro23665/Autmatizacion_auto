import sys
import os

# Add src to path for both development and bundled modes
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in development
    base_path = os.path.dirname(os.path.abspath(__file__))

src_path = os.path.join(base_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gui_v2 import main

if __name__ == '__main__':
    main()