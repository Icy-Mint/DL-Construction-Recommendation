"""
Baseline Generator - A tool for converting building energy rules to structured JSON.

This package provides tools for parsing regulatory-style building energy rules
into structured JSON logic without using copyrighted content.
"""

__version__ = "0.1.0"

from .schema import RuleSchema, Rule, Condition, Action
from .parser import RuleParser
from .engine import BaselineEngine

__all__ = [
    "RuleSchema",
    "Rule",
    "Condition",
    "Action",
    "RuleParser",
    "BaselineEngine",
]
