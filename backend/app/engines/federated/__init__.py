"""
MuleTrace AI — Federated Graph Learning Package.

Exports the federated coordinator, local graph trainer, differential privacy engine,
and privacy-preserving alert correlator.
"""

from __future__ import annotations


from app.engines.federated.alert_correlator import alert_correlator
from app.engines.federated.coordinator import coordinator
from app.engines.federated.local_trainer import local_trainer
from app.engines.federated.privacy import dp_engine, secure_agg_engine

__all__ = [
    "alert_correlator",
    "coordinator",
    "dp_engine",
    "local_trainer",
    "secure_agg_engine",
]
