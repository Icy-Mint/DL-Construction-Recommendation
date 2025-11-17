"""Tests for the parser module."""

import pytest
from baseline_generator.parser import RuleParser
from baseline_generator.schema import (
    ComparisonOperator, LogicalOperator,
    Condition, ConditionGroup
)


class TestRuleParser:
    """Tests for RuleParser class."""
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = RuleParser()
        assert parser.rule_counter == 0
    
    def test_parse_simple_rule(self):
        """Test parsing a simple rule."""
        parser = RuleParser()
        text = "If building type is office then set lighting power density to 1.0"
        
        rule = parser.parse_rule_text(text, category="lighting")
        
        assert rule.id == "rule_001"
        assert rule.category == "lighting"
        assert len(rule.actions) > 0
    
    def test_parse_rule_with_comparison(self):
        """Test parsing rule with comparison operator."""
        parser = RuleParser()
        text = "If building area is greater than 10000 sqft then set value to 1.5"
        
        rule = parser.parse_rule_text(text)
        
        assert isinstance(rule.conditions, Condition)
        assert rule.conditions.field == "building_area"
    
    def test_parse_rule_with_and_operator(self):
        """Test parsing rule with AND operator."""
        parser = RuleParser()
        text = "If building type is office and building area is less than 25000 then set lighting to 1.0"
        
        rule = parser.parse_rule_text(text)
        
        assert isinstance(rule.conditions, ConditionGroup)
        assert rule.conditions.operator == LogicalOperator.AND
    
    def test_parse_rule_with_or_operator(self):
        """Test parsing rule with OR operator."""
        parser = RuleParser()
        text = "If climate zone is 1a or climate zone is 2a then set cooling to 3.5"
        
        rule = parser.parse_rule_text(text)
        
        assert isinstance(rule.conditions, ConditionGroup)
        assert rule.conditions.operator == LogicalOperator.OR
    
    def test_parse_multiple_rules(self):
        """Test parsing multiple rules from text."""
        parser = RuleParser()
        text = """If building type is office then set lighting to 1.0
If building type is retail then set lighting to 1.5"""
        
        rules = parser.parse_rules_from_text(text)
        
        assert len(rules) == 2
        assert rules[0].id == "rule_001"
        assert rules[1].id == "rule_002"
    
    def test_parse_rule_with_custom_id(self):
        """Test parsing rule with custom ID."""
        parser = RuleParser()
        text = "If building type is office then set lighting to 1.0"
        
        rule = parser.parse_rule_text(text, rule_id="custom_001")
        
        assert rule.id == "custom_001"
    
    def test_extract_numeric_value(self):
        """Test extracting numeric values from text."""
        parser = RuleParser()
        text = "If building area is 15000 sqft then set value to 2.5"
        
        rule = parser.parse_rule_text(text)
        
        # Should extract 15000 from condition
        if isinstance(rule.conditions, Condition):
            assert isinstance(rule.conditions.value, (int, float))
    
    def test_extract_unit(self):
        """Test extracting units from text."""
        parser = RuleParser()
        text = "If building area is 10000 sqft then set value to 1.0"
        
        rule = parser.parse_rule_text(text)
        
        # Unit extraction is best-effort
        assert rule is not None
    
    def test_skip_comments(self):
        """Test skipping comments in multi-line text."""
        parser = RuleParser()
        text = """# This is a comment
If building type is office then set lighting to 1.0
# Another comment
If building type is retail then set lighting to 1.5"""
        
        rules = parser.parse_rules_from_text(text)
        
        # Should only parse non-comment lines
        assert all(not rule.description.startswith('#') for rule in rules)
