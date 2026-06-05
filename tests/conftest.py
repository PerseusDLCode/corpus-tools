import sys
import os
from pathlib import Path
import pytest

from tei import TEIDocument


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the src directory
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Print paths for debugging
print(f"Python path: {sys.path}")


@pytest.fixture
def thucydides():
    return TEIDocument(Path("tlg0003.tlg001.perseus-grc2.xml"))
