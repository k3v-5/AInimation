import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.run_f76_real_blender_validation import run_f76_real_blender_validation

if __name__ == "__main__":
    run_f76_real_blender_validation()
