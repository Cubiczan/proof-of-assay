"""Proof-of-Assay: verifiable mining-payables audit (fixture/local mode)."""
from .audit import audit_lot, load_fixtures, run_audit
from .chain import build_chain, verify_chain
__all__ = ["audit_lot", "load_fixtures", "run_audit", "build_chain", "verify_chain"]
__version__ = "0.1.0"
