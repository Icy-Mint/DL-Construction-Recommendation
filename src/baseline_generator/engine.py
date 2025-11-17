"""
Baseline rule engine for evaluating and applying building energy rules.

This module provides the engine for evaluating rules against building specifications
and generating baseline model specifications.
"""

from typing import Dict, Any, List, Optional, Union
from .schema import (
    Rule, RuleSchema, Condition, ConditionGroup, Action,
    ComparisonOperator, LogicalOperator
)


class BaselineEngine:
    """Engine for evaluating rules and generating baseline specifications."""
    
    def __init__(self, rule_schema: Optional[RuleSchema] = None):
        """Initialize the engine with a rule schema.
        
        Args:
            rule_schema: RuleSchema containing rules to evaluate
        """
        self.rule_schema = rule_schema
        self.rules = rule_schema.rules if rule_schema else []
    
    def load_rules(self, rule_schema: RuleSchema):
        """Load rules from a RuleSchema.
        
        Args:
            rule_schema: RuleSchema to load
        """
        self.rule_schema = rule_schema
        self.rules = rule_schema.rules
    
    def evaluate(self, building_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate building specification against all rules and generate baseline.
        
        Args:
            building_spec: Dictionary containing building properties
            
        Returns:
            Dictionary containing baseline specifications
        """
        baseline = {
            "input": building_spec,
            "matched_rules": [],
            "baseline_properties": {},
            "evaluation_log": []
        }
        
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if self.evaluate_rule(rule, building_spec):
                baseline["matched_rules"].append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "category": rule.category
                })
                
                # Apply actions
                self._apply_actions(rule.actions, baseline["baseline_properties"], building_spec)
                
                baseline["evaluation_log"].append({
                    "rule_id": rule.id,
                    "status": "matched",
                    "message": f"Rule '{rule.name}' matched and applied"
                })
            else:
                baseline["evaluation_log"].append({
                    "rule_id": rule.id,
                    "status": "not_matched",
                    "message": f"Rule '{rule.name}' conditions not met"
                })
        
        return baseline
    
    def evaluate_rule(self, rule: Rule, building_spec: Dict[str, Any]) -> bool:
        """Evaluate if a rule matches the building specification.
        
        Args:
            rule: Rule to evaluate
            building_spec: Building specification dictionary
            
        Returns:
            True if rule conditions are met, False otherwise
        """
        if isinstance(rule.conditions, Condition):
            return self._evaluate_condition(rule.conditions, building_spec)
        elif isinstance(rule.conditions, ConditionGroup):
            return self._evaluate_condition_group(rule.conditions, building_spec)
        else:
            return False
    
    def _evaluate_condition(self, condition: Condition, building_spec: Dict[str, Any]) -> bool:
        """Evaluate a single condition.
        
        Args:
            condition: Condition to evaluate
            building_spec: Building specification dictionary
            
        Returns:
            True if condition is met, False otherwise
        """
        # Get the field value from building spec
        field_value = building_spec.get(condition.field)
        
        if field_value is None:
            return False
        
        # Evaluate based on operator
        operator = condition.operator
        target_value = condition.value
        
        try:
            if operator == ComparisonOperator.EQUALS:
                return field_value == target_value
            elif operator == ComparisonOperator.NOT_EQUALS:
                return field_value != target_value
            elif operator == ComparisonOperator.GREATER_THAN:
                return float(field_value) > float(target_value)
            elif operator == ComparisonOperator.LESS_THAN:
                return float(field_value) < float(target_value)
            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return float(field_value) >= float(target_value)
            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                return float(field_value) <= float(target_value)
            elif operator == ComparisonOperator.IN:
                return field_value in target_value
            elif operator == ComparisonOperator.NOT_IN:
                return field_value not in target_value
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    def _evaluate_condition_group(self, group: ConditionGroup, 
                                  building_spec: Dict[str, Any]) -> bool:
        """Evaluate a group of conditions.
        
        Args:
            group: ConditionGroup to evaluate
            building_spec: Building specification dictionary
            
        Returns:
            True if group conditions are met, False otherwise
        """
        results = []
        
        for condition in group.conditions:
            if isinstance(condition, Condition):
                results.append(self._evaluate_condition(condition, building_spec))
            elif isinstance(condition, ConditionGroup):
                results.append(self._evaluate_condition_group(condition, building_spec))
        
        # Apply logical operator
        if group.operator == LogicalOperator.AND:
            return all(results)
        elif group.operator == LogicalOperator.OR:
            return any(results)
        elif group.operator == LogicalOperator.NOT:
            return not any(results)
        else:
            return False
    
    def _apply_actions(self, actions: List[Action], 
                      baseline_properties: Dict[str, Any],
                      building_spec: Dict[str, Any]):
        """Apply actions to baseline properties.
        
        Args:
            actions: List of actions to apply
            baseline_properties: Dictionary to store baseline properties
            building_spec: Original building specification
        """
        for action in actions:
            if action.action_type == "set_value":
                baseline_properties[action.target] = action.value
            elif action.action_type == "apply_method":
                # Store method reference
                baseline_properties[action.target] = {
                    "method": action.value,
                    "parameters": action.parameters
                }
            elif action.action_type == "reference_table":
                # Store table reference
                baseline_properties[action.target] = {
                    "table": action.value,
                    "parameters": action.parameters
                }
            elif action.action_type == "evaluate":
                # Store evaluation result
                baseline_properties[action.target] = action.value
            else:
                # Generic action storage
                if action.target not in baseline_properties:
                    baseline_properties[action.target] = {}
                baseline_properties[action.target] = {
                    "action_type": action.action_type,
                    "value": action.value,
                    "parameters": action.parameters
                }
    
    def generate_baseline(self, building_spec: Dict[str, Any], 
                         output_format: str = "json") -> Union[Dict[str, Any], str]:
        """Generate baseline model specification from building specification.
        
        Args:
            building_spec: Dictionary containing building properties
            output_format: Output format ("json" or "yaml")
            
        Returns:
            Baseline specification in requested format
        """
        baseline = self.evaluate(building_spec)
        
        if output_format == "yaml":
            import yaml
            return yaml.dump(baseline, default_flow_style=False, sort_keys=False)
        else:
            return baseline
    
    def get_applicable_rules(self, building_spec: Dict[str, Any]) -> List[Rule]:
        """Get list of rules that apply to a building specification.
        
        Args:
            building_spec: Dictionary containing building properties
            
        Returns:
            List of applicable rules
        """
        applicable = []
        for rule in self.rules:
            if self.evaluate_rule(rule, building_spec):
                applicable.append(rule)
        return applicable
    
    def validate_building_spec(self, building_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a building specification.
        
        Args:
            building_spec: Dictionary containing building properties
            
        Returns:
            Validation result with errors and warnings
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for required fields based on rules
        required_fields = set()
        for rule in self.rules:
            required_fields.update(self._get_required_fields(rule.conditions))
        
        for field in required_fields:
            if field not in building_spec:
                result["warnings"].append(f"Missing field: {field}")
        
        return result
    
    def _get_required_fields(self, conditions: Union[Condition, ConditionGroup]) -> List[str]:
        """Extract required fields from conditions.
        
        Args:
            conditions: Condition or ConditionGroup
            
        Returns:
            List of required field names
        """
        fields = []
        
        if isinstance(conditions, Condition):
            fields.append(conditions.field)
        elif isinstance(conditions, ConditionGroup):
            for cond in conditions.conditions:
                fields.extend(self._get_required_fields(cond))
        
        return fields
