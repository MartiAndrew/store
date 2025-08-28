from pathlib import Path
from tempfile import gettempdir

PROJECT_ROOT = Path(__file__).absolute().parent.parent.parent
TEMP_DIR = Path(gettempdir())
