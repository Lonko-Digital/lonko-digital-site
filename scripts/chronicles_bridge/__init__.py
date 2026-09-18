"""Chronicles Drive publishing bridge — intake for v4 article packages."""

from .ingest import IngestResult, ingest_inbox

__all__ = ["IngestResult", "ingest_inbox"]
