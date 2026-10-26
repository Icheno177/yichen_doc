"""Independent, evidence-led audits for research deliverables.

The audit package deliberately separates source completeness, presentation
mapping, evidence, calculations, package structure and rendered-page review.
Candidate similarity is never represented as verified retention.
"""

from .engine import audit_transition

__all__ = ["audit_transition"]
