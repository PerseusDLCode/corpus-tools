import sys
from pathlib import Path
import pytest

from tei import TEIDocument


# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the src directory
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def tlg0001_tlg001_perseus_grc2(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0001.tlg001.perseus-grc2.xml")


@pytest.fixture
def tlg0003_tlg001_perseus_grc2(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0003.tlg001.perseus-grc2.xml")


@pytest.fixture
def thucydides_grc(tlg0003_tlg001_perseus_grc2):
    return tlg0003_tlg001_perseus_grc2


@pytest.fixture
def tlg0011_tlg001_perseus_grc2(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0011.tlg001.perseus-grc2.xml")


@pytest.fixture
def tlg0057_tlg069_1st1K_grc1(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0057.tlg069.1st1K-grc1.xml")


@pytest.fixture
def tlg0086_tlg034_perseus_grc2(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0086.tlg034.perseus-grc2.xml")


@pytest.fixture
def tlg0086_tlg034_perseus_eng2(shared_datadir):
    return TEIDocument(shared_datadir / "tlg0086.tlg034.perseus-eng2.xml")


@pytest.fixture
def phi1017_phi007_perseus_lat2(shared_datadir):
    return TEIDocument(shared_datadir / "phi1017.phi007.perseus-lat2.xml")


@pytest.fixture
def phi2331_phi013_perseus_lat2(shared_datadir):
    return TEIDocument(shared_datadir / "phi2331.phi013.perseus-lat2.xml")
