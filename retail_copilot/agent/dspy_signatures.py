from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass


# These are lightweight signatures / simple dataclasses to mimic DSPy-style interfaces.
# They are used by the graph to pass structured data between nodes.

@dataclass
class RouterOutput:
    route: str  # 'rag', 'sql', or 'hybrid'
    reason: str


@dataclass
class RetrievalOutput:
    chunks: List[Dict[str, Any]]


@dataclass
class PlannerOutput:
    # Extracted constraints: date ranges, categories, KPI formula etc.
    date_from: Optional[str]
    date_to: Optional[str]
    categories: List[str]
    kpi: Optional[str]
    notes: Dict[str, Any]


@dataclass
class NL2SQLOutput:
    sql: str


@dataclass
class ExecOutput:
    columns: List[str]
    rows: List[Dict[str, Any]]
    error: str


@dataclass
class SynthOutput:
    final_answer: Any
    citations: List[str]
    explanation: str
    confidence: float
