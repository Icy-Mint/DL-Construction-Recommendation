"""Tests for the schema module."""

import pytest
from baseline_generator.schema import (
    Rule, Condition, ConditionGroup, Action, RuleSchema,
    ComparisonOperator, LogicalOperator
)


class TestCondition:
    """Tests for Condition class."""
    
    def test_condition_creation(self):
        """Test creating a condition."""
        condition = Condition(
            field="building_area",
            operator=ComparisonOperator.GREATER_THAN,
            value=10000,
            unit="sqft"
        )
        
        assert condition.field == "building_area"
        assert condition.operator == ComparisonOperator.GREATER_THAN
        assert condition.value == 10000
        assert condition.unit == "sqft"
    
    def test_condition_to_dict(self):
        """Test converting condition to dictionary."""
        condition = Condition(
            field="climate_zone",
            operator=ComparisonOperator.EQUALS,
            value="5a"
        )
        
        result = condition.to_dict()
        assert result["field"] == "climate_zone"
        assert result["operator"] == "equals"
        assert result["value"] == "5a"


class TestConditionGroup:
    """Tests for ConditionGroup class."""
    
    def test_condition_group_creation(self):
        """Test creating a condition group."""
        cond1 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        cond2 = Condition("building_area", ComparisonOperator.LESS_THAN, 25000)
        
        group = ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[cond1, cond2]
        )
        
        assert group.operator == LogicalOperator.AND
        assert len(group.conditions) == 2
    
    def test_condition_group_to_dict(self):
        """Test converting condition group to dictionary."""
        cond1 = Condition("building_type", ComparisonOperator.EQUALS, "office")
        cond2 = Condition("building_area", ComparisonOperator.LESS_THAN, 25000)
        
        group = ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[cond1, cond2]
        )
        
        result = group.to_dict()
        assert result["operator"] == "and"
        assert len(result["conditions"]) == 2


class TestAction:
    """Tests for Action class."""
    
    def test_action_creation(self):
        """Test creating an action."""
        action = Action(
            action_type="set_value",
            target="lighting_power_density",
            value=1.0,
            parameters={"unit": "W/sqft"}
        )
        
        assert action.action_type == "set_value"
        assert action.target == "lighting_power_density"
        assert action.value == 1.0
        assert action.parameters["unit"] == "W/sqft"
    
    def test_action_to_dict(self):
        """Test converting action to dictionary."""
        action = Action(
            action_type="set_value",
            target="cooling_cop",
            value=3.5
        )
        
        result = action.to_dict()
        assert result["action_type"] == "set_value"
        assert result["target"] == "cooling_cop"
        assert result["value"] == 3.5


class TestRule:
    """Tests for Rule class."""
    
    def test_rule_creation(self):
        """Test creating a rule."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        
        rule = Rule(
            id="r001",
            name="Test Rule",
            description="A test rule",
            category="lighting",
            conditions=condition,
            actions=[action],
            priority=10
        )
        
        assert rule.id == "r001"
        assert rule.name == "Test Rule"
        assert rule.category == "lighting"
        assert rule.priority == 10
    
    def test_rule_to_dict(self):
        """Test converting rule to dictionary."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        
        rule = Rule(
            id="r001",
            name="Test Rule",
            description="A test rule",
            category="lighting",
            conditions=condition,
            actions=[action]
        )
        
        result = rule.to_dict()
        assert result["id"] == "r001"
        assert result["name"] == "Test Rule"
        assert "conditions" in result
        assert "actions" in result


class TestRuleSchema:
    """Tests for RuleSchema class."""
    
    def test_schema_creation(self):
        """Test creating a rule schema."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        
        schema = RuleSchema(
            version="1.0",
            rules=[rule],
            metadata={"description": "Test schema"}
        )
        
        assert schema.version == "1.0"
        assert len(schema.rules) == 1
        assert schema.metadata["description"] == "Test schema"
    
    def test_schema_to_dict(self):
        """Test converting schema to dictionary."""
        condition = Condition("building_type", ComparisonOperator.EQUALS, "office")
        action = Action("set_value", "lighting_power_density", 1.0)
        rule = Rule("r001", "Test Rule", "A test rule", "lighting", condition, [action])
        
        schema = RuleSchema(version="1.0", rules=[rule])
        result = schema.to_dict()
        
        assert result["version"] == "1.0"
        assert len(result["rules"]) == 1
    
    def test_schema_from_dict(self):
        """Test creating schema from dictionary."""
        data = {
            "version": "1.0",
            "rules": [
                {
                    "id": "r001",
                    "name": "Test Rule",
                    "description": "A test rule",
                    "category": "lighting",
                    "conditions": {
                        "field": "building_type",
                        "operator": "equals",
                        "value": "office"
                    },
                    "actions": [
                        {
                            "action_type": "set_value",
                            "target": "lighting_power_density",
                            "value": 1.0
                        }
                    ]
                }
            ]
        }
        
        schema = RuleSchema.from_dict(data)
        assert schema.version == "1.0"
        assert len(schema.rules) == 1
        assert schema.rules[0].id == "r001"
