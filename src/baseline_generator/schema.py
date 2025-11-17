"""
Rule schema definitions for building energy rules.

This module defines the structure for representing building energy compliance rules
as structured data. No copyrighted ASHRAE content is included.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class ComparisonOperator(str, Enum):
    """Comparison operators for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class Condition:
    """Represents a single condition in a rule.
    
    Attributes:
        field: The property being evaluated (e.g., "building_area", "climate_zone")
        operator: The comparison operator
        value: The value to compare against
        unit: Optional unit of measurement (e.g., "sqft", "degF")
    """
    field: str
    operator: ComparisonOperator
    value: Union[str, int, float, List[Any]]
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary."""
        result = {
            "field": self.field,
            "operator": self.operator.value if isinstance(self.operator, ComparisonOperator) else self.operator,
            "value": self.value
        }
        if self.unit:
            result["unit"] = self.unit
        return result


@dataclass
class ConditionGroup:
    """Represents a group of conditions combined with a logical operator.
    
    Attributes:
        operator: Logical operator (AND, OR, NOT)
        conditions: List of conditions or nested condition groups
    """
    operator: LogicalOperator
    conditions: List[Union[Condition, 'ConditionGroup']] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition group to dictionary."""
        return {
            "operator": self.operator.value if isinstance(self.operator, LogicalOperator) else self.operator,
            "conditions": [
                c.to_dict() if hasattr(c, 'to_dict') else c
                for c in self.conditions
            ]
        }


@dataclass
class Action:
    """Represents an action to be taken when a rule matches.
    
    Attributes:
        action_type: Type of action (e.g., "set_value", "apply_method", "reference_table")
        target: The property to be modified
        value: The value to set or method to apply
        parameters: Additional parameters for the action
    """
    action_type: str
    target: str
    value: Union[str, int, float, Dict[str, Any]]
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        result = {
            "action_type": self.action_type,
            "target": self.target,
            "value": self.value
        }
        if self.parameters:
            result["parameters"] = self.parameters
        return result


@dataclass
class Rule:
    """Represents a complete building energy rule.
    
    Attributes:
        id: Unique identifier for the rule
        name: Human-readable name
        description: Description of what the rule does
        category: Category of the rule (e.g., "lighting", "hvac", "envelope")
        conditions: Conditions that must be met for the rule to apply
        actions: Actions to take when conditions are met
        priority: Priority for rule application (higher = earlier)
        metadata: Additional metadata about the rule
    """
    id: str
    name: str
    description: str
    category: str
    conditions: Union[Condition, ConditionGroup]
    actions: List[Action]
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "conditions": self.conditions.to_dict() if hasattr(self.conditions, 'to_dict') else self.conditions,
            "actions": [action.to_dict() for action in self.actions],
            "priority": self.priority
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class RuleSchema:
    """Schema for a collection of rules.
    
    Attributes:
        version: Schema version
        rules: List of rules
        metadata: Metadata about the rule set
    """
    version: str
    rules: List[Rule]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary."""
        result = {
            "version": self.version,
            "rules": [rule.to_dict() for rule in self.rules]
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleSchema':
        """Create RuleSchema from dictionary."""
        rules = []
        for rule_data in data.get("rules", []):
            # Parse conditions
            conditions_data = rule_data["conditions"]
            if "operator" in conditions_data and "conditions" in conditions_data:
                # It's a ConditionGroup
                conditions = cls._parse_condition_group(conditions_data)
            else:
                # It's a single Condition
                conditions = cls._parse_condition(conditions_data)
            
            # Parse actions
            actions = [
                Action(
                    action_type=action_data["action_type"],
                    target=action_data["target"],
                    value=action_data["value"],
                    parameters=action_data.get("parameters", {})
                )
                for action_data in rule_data["actions"]
            ]
            
            rule = Rule(
                id=rule_data["id"],
                name=rule_data["name"],
                description=rule_data["description"],
                category=rule_data["category"],
                conditions=conditions,
                actions=actions,
                priority=rule_data.get("priority", 0),
                metadata=rule_data.get("metadata", {})
            )
            rules.append(rule)
        
        return cls(
            version=data["version"],
            rules=rules,
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def _parse_condition(cls, data: Dict[str, Any]) -> Condition:
        """Parse a single condition from dictionary."""
        return Condition(
            field=data["field"],
            operator=ComparisonOperator(data["operator"]),
            value=data["value"],
            unit=data.get("unit")
        )
    
    @classmethod
    def _parse_condition_group(cls, data: Dict[str, Any]) -> ConditionGroup:
        """Parse a condition group from dictionary."""
        conditions = []
        for cond_data in data["conditions"]:
            if "operator" in cond_data and "conditions" in cond_data:
                conditions.append(cls._parse_condition_group(cond_data))
            else:
                conditions.append(cls._parse_condition(cond_data))
        
        return ConditionGroup(
            operator=LogicalOperator(data["operator"]),
            conditions=conditions
        )
