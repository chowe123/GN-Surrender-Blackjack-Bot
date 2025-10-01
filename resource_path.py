import os, sys

def resource_path(relative_path):
    """Get absolute path to resource, works in dev and in PyInstaller exe."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # If running from exe, use the folder where the exe is located
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)