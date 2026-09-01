import sys
from pathlib import Path

# Add backend and project root directories to sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))
