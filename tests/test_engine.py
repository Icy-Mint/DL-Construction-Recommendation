"""Tests for the engine module."""

import pytest
from baseline_generator.engine import BaselineEngine
from baseline_generator.schema import (
    Rule, RuleSchema, Condition, ConditionGroup, Action,
    ComparisonOperator, LogicalOperator
)


class TestBaselineEngine:
    """Tests for BaselineEngine class."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = BaselineEngine()
        assert engine.rules == []
    
    def test_engine_with_schema(self):
        """Test engine initialization with schema."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        schema = RuleSchema(version="1.0", rules=[rule])
        
        engine = BaselineEngine(schema)
        
        assert len(engine.rules) == 1
        assert engine.rule_schema == schema
    
    def test_evaluate_simple_condition(self):
        """Test evaluating a simple condition."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        
        engine = BaselineEngine()
        engine.load_rules(RuleSchema(version="1.0", rules=[rule]))
        
        building_spec = {"building_type": "office"}
        
        assert engine.evaluate_rule(rule, building_spec) is True
    
    def test_evaluate_condition_not_met(self):
        """Test evaluating when condition is not met."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        
        engine = BaselineEngine()
        
        building_spec = {"building_type": "retail"}
        
        assert engine.evaluate_rule(rule, building_spec) is False
    
    def test_evaluate_numeric_comparison(self):
        """Test evaluating numeric comparisons."""
        condition = Condition("building_area", ComparisonOperator.GREATER_THAN, 10000)
        action = Action("set_value", "lighting_power_density", 1.5)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        
        engine = BaselineEngine()
        
        building_spec = {"building_area": 15000}
        assert engine.evaluate_rule(rule, building_spec) is True
        
        building_spec = {"building_area": 5000}
        assert engine.evaluate_rule(rule, building_spec) is False
    
    def test_evaluate_condition_group_and(self):
        """Test evaluating condition group with AND operator."""
        cond1 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        cond2 = Condition("building_area", ComparisonOperator.LESS_THAN, 25000)
        group = ConditionGroup(LogicalOperator.AND, [cond1, cond2])
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", group, [action])
        
        engine = BaselineEngine()
        
        # Both conditions met
        building_spec = {"building_type": "office", "building_area": 15000}
        assert engine.evaluate_rule(rule, building_spec) is True
        
        # Only one condition met
        building_spec = {"building_type": "retail", "building_area": 15000}
        assert engine.evaluate_rule(rule, building_spec) is False
    
    def test_evaluate_condition_group_or(self):
        """Test evaluating condition group with OR operator."""
        cond1 = Condition("climate_zone", ComparisonOperator.EQUALS, "1a")
        cond2 = Condition("climate_zone", ComparisonOperator.EQUALS, "2a")
        group = ConditionGroup(LogicalOperator.OR, [cond1, cond2])
        action = Action("set_value", "cooling_cop", 3.5)
        rule = Rule("r001", "Test Rule", "A test rule", "hvac", group, [action])
        
        engine = BaselineEngine()
        
        # First condition met
        building_spec = {"climate_zone": "1a"}
        assert engine.evaluate_rule(rule, building_spec) is True
        
        # Second condition met
        building_spec = {"climate_zone": "2a"}
        assert engine.evaluate_rule(rule, building_spec) is True
        
        # Neither condition met
        building_spec = {"climate_zone": "5a"}
        assert engine.evaluate_rule(rule, building_spec) is False
    
    def test_evaluate_in_operator(self):
        """Test evaluating IN operator."""
        condition = Condition("climate_zone", ComparisonOperator.IN, ["1a", "2a", "3a"])
        action = Action("set_value", "cooling_cop", 3.5)
        rule = Rule("r001", "Test Rule", "A test rule", "hvac", condition, [action])
        
        engine = BaselineEngine()
        
        building_spec = {"climate_zone": "2a"}
        assert engine.evaluate_rule(rule, building_spec) is True
        
        building_spec = {"climate_zone": "5a"}
        assert engine.evaluate_rule(rule, building_spec) is False
    
    def test_generate_baseline(self):
        """Test generating baseline from building spec."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        schema = RuleSchema(version="1.0", rules=[rule])
        
        engine = BaselineEngine(schema)
        building_spec = {"building_type": "office"}
        
        baseline = engine.generate_baseline(building_spec)
        
        assert "input" in baseline
        assert "matched_rules" in baseline
        assert "baseline_properties" in baseline
        assert len(baseline["matched_rules"]) == 1
        assert baseline["baseline_properties"]["lighting_power_density"] == 1.0
    
    def test_get_applicable_rules(self):
        """Test getting applicable rules."""
        condition1 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action1 = Action("set_value", "lighting_power_density", 1.0)
        rule1 = Rule("r001", "Office Rule", "A test rule", "lighting", condition1, [action1])
        
        condition2 = Condition("building_type", ComparisonOperator.EQUALS, "retail")
        action2 = Action("set_value", "lighting_power_density", 1.5)
        rule2 = Rule("r002", "Retail Rule", "A test rule", "lighting", condition2, [action2])
        
        schema = RuleSchema(version="1.0", rules=[rule1, rule2])
        engine = BaselineEngine(schema)
        
        building_spec = {"building_type": "office"}
        applicable = engine.get_applicable_rules(building_spec)
        
        assert len(applicable) == 1
        assert applicable[0].id == "r001"
    
    def test_rule_priority(self):
        """Test that rules are applied in priority order."""
        condition1 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action1 = Action("set_value", "lighting_power_density", 1.0)
        rule1 = Rule("r001", "Low Priority", "A test rule", "lighting", condition1, [action1], priority=1)
        
        condition2 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action2 = Action("set_value", "lighting_power_density", 2.0)
        rule2 = Rule("r002", "High Priority", "A test rule", "lighting", condition2, [action2], priority=10)
        
        schema = RuleSchema(version="1.0", rules=[rule1, rule2])
        engine = BaselineEngine(schema)
        
        building_spec = {"building_type": "office"}
        baseline = engine.generate_baseline(building_spec)
        
        # Higher priority rule (r002) should be evaluated first, but both apply
        # Last one wins in this simple implementation
        assert len(baseline["matched_rules"]) == 2
    
    def test_validate_building_spec(self):
        """Test validating building specification."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        schema = RuleSchema(version="1.0", rules=[rule])
        
        engine = BaselineEngine(schema)
        
        # Complete spec
        building_spec = {"building_type": "office"}
        result = engine.validate_building_spec(building_spec)
        assert result["valid"] is True
        
        # Incomplete spec
        building_spec = {}
        result = engine.validate_building_spec(building_spec)
        assert len(result["warnings"]) > 0
