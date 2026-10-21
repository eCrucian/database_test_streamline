import hashlib
from importlib import resources

from dbts.extract.javascript import JavaScriptExtractor
from dbts.extract.pyspark import PySparkExtractor
from dbts.extract.sql import SQLExtractor
from dbts.extract.terraform import TerraformExtractor
from dbts.ports import Extractor

EXTRACTORS: tuple[Extractor, ...] = (
    SQLExtractor(),
    PySparkExtractor(),
    TerraformExtractor(),
    JavaScriptExtractor(),
)


def extractors_fingerprint() -> str:
    """Hash do código dos extratores: muda quando a lógica de extração muda."""
    files = sorted(
        (f for f in resources.files("dbts.extract").iterdir() if f.name.endswith(".py")),
        key=lambda f: f.name,
    )
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.name.encode() + file.read_bytes())
    return digest.hexdigest()[:16]
