#!/usr/bin/env python3
"""
Command-line interface for baseline generator.

Usage:
    generate_baseline input.yaml [--output output.json] [--format json|yaml]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

from baseline_generator import RuleSchema, BaselineEngine, RuleParser


def load_yaml_file(file_path: str) -> dict:
    """Load YAML file.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Parsed YAML content as dictionary
    """
    if yaml is None:
        print("Error: PyYAML is required to read YAML files. Install it with: pip install pyyaml")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_json_file(file_path: str) -> dict:
    """Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON content as dictionary
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def save_output(data: dict, file_path: str, format_type: str):
    """Save output to file.
    
    Args:
        data: Data to save
        file_path: Output file path
        format_type: Format type (json or yaml)
    """
    with open(file_path, 'w') as f:
        if format_type == 'yaml':
            if yaml is None:
                print("Warning: PyYAML not installed, saving as JSON instead")
                json.dump(data, f, indent=2)
            else:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(data, f, indent=2)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate baseline building energy model from specifications',
        epilog='Example: generate_baseline input.yaml --output baseline.json'
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Input YAML or JSON file with building specification'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['json', 'yaml'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--rules', '-r',
        type=str,
        default=None,
        help='Path to rules JSON file (optional, uses built-in rules if not specified)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Load input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    if args.verbose:
        print(f"Loading input from: {args.input_file}")
    
    # Determine file format and load
    if input_path.suffix.lower() in ['.yaml', '.yml']:
        building_spec = load_yaml_file(args.input_file)
    elif input_path.suffix.lower() == '.json':
        building_spec = load_json_file(args.input_file)
    else:
        print(f"Error: Unsupported file format '{input_path.suffix}'. Use .yaml, .yml, or .json")
        sys.exit(1)
    
    # Load rules if specified
    rule_schema = None
    if args.rules:
        rules_path = Path(args.rules)
        if not rules_path.exists():
            print(f"Error: Rules file '{args.rules}' not found")
            sys.exit(1)
        
        if args.verbose:
            print(f"Loading rules from: {args.rules}")
        
        rules_data = load_json_file(args.rules)
        rule_schema = RuleSchema.from_dict(rules_data)
    else:
        # Use default/example rules
        if args.verbose:
            print("No rules file specified, using default rules")
        rule_schema = create_default_rules()
    
    # Create engine and generate baseline
    engine = BaselineEngine(rule_schema)
    
    if args.verbose:
        print(f"Evaluating {len(engine.rules)} rules...")
    
    baseline = engine.generate_baseline(building_spec, output_format='dict')
    
    # Output results
    if args.output:
        save_output(baseline, args.output, args.format)
        if args.verbose:
            print(f"Baseline saved to: {args.output}")
    else:
        # Print to stdout
        if args.format == 'yaml' and yaml is not None:
            print(yaml.dump(baseline, default_flow_style=False, sort_keys=False))
        else:
            print(json.dumps(baseline, indent=2))
    
    if args.verbose:
        matched = len(baseline.get('matched_rules', []))
        total = len(engine.rules)
        print(f"\nMatched {matched} out of {total} rules")


def create_default_rules() -> RuleSchema:
    """Create a default set of rules for demonstration.
    
    Returns:
        RuleSchema with example rules
    """
    from baseline_generator.schema import (
        Rule, Condition, ConditionGroup, Action,
        ComparisonOperator, LogicalOperator
    )
    
    # Example rule: Small office buildings
    rule1 = Rule(
        id="r001",
        name="Small Office Building Baseline",
        description="Baseline specifications for small office buildings",
        category="building_type",
        conditions=ConditionGroup(
            operator=LogicalOperator.AND,
            conditions=[
                Condition(
                    field="building_type",
                    operator=ComparisonOperator.EQUALS,
                    value="office"
                ),
                Condition(
                    field="building_area",
                    operator=ComparisonOperator.LESS_THAN,
                    value=25000,
                    unit="sqft"
                )
            ]
        ),
        actions=[
            Action(
                action_type="set_value",
                target="lighting_power_density",
                value=1.0,
                parameters={"unit": "W/sqft"}
            )
        ],
        priority=10
    )
    
    # Example rule: Climate zone specific
    rule2 = Rule(
        id="r002",
        name="Hot Climate HVAC Efficiency",
        description="HVAC efficiency requirements for hot climates",
        category="hvac",
        conditions=Condition(
            field="climate_zone",
            operator=ComparisonOperator.IN,
            value=["1a", "1b", "2a", "2b"]
        ),
        actions=[
            Action(
                action_type="set_value",
                target="cooling_cop",
                value=3.5,
                parameters={"unit": "dimensionless"}
            )
        ],
        priority=5
    )
    
    return RuleSchema(
        version="1.0",
        rules=[rule1, rule2],
        metadata={
            "description": "Default example rules for building energy baselines",
            "note": "These are synthetic examples only, not based on copyrighted standards"
        }
    )


if __name__ == '__main__':
    main()
