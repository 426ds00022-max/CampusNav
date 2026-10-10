"""
Root entry point for Campus Navigator.
Allows running `python app.py` directly from the project root folder.
"""
import os
import sys

# Add CampusNavigator folder to path
current_dir = os.path.dirname(os.path.abspath(__file__))
campus_dir = os.path.join(current_dir, "CampusNavigator")
if campus_dir not in sys.path:
    sys.path.insert(0, campus_dir)

from CampusNavigator.app import app

if __name__ == "__main__":
    print("=" * 60)
    print(" Campus Navigator - Starting from Root Directory")
    print(" Available at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
