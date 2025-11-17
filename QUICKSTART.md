# Quick Start Guide

This guide will help you get started with the Baseline Generator in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/Icy-Mint/Baseline-Model-Auto-Generation-.git
cd Baseline-Model-Auto-Generation-

# Install the package
pip install -e .
```

## Basic Usage

### 1. Using the CLI

Generate a baseline from a building specification:

```bash
generate_baseline examples/example_building_spec.yaml
```

Save the output to a file:

```bash
generate_baseline examples/example_building_spec.yaml --output baseline.json
```

Use custom rules:

```bash
generate_baseline examples/example_building_spec.yaml \
  --rules examples/example_rules.json \
  --output baseline.json
```

### 2. Using Python API

```python
from baseline_generator import RuleParser, RuleSchema, BaselineEngine
import json

# Parse text rules
parser = RuleParser()
rule_text = "If building type is office and building area is less than 25000 sqft then set lighting power density to 1.0 W/sqft"
rule = parser.parse_rule_text(rule_text, category="lighting")

# Create schema
schema = RuleSchema(version="1.0", rules=[rule])

# Generate baseline
engine = BaselineEngine(schema)
building_spec = {
    "building_type": "office",
    "building_area": 15000
}

baseline = engine.generate_baseline(building_spec)
print(json.dumps(baseline, indent=2))
```

## Creating Your Own Rules

### Option 1: Write Text Rules

Create a text file with natural language rules (one per line):

```
If building type is office and building area is less than 25000 sqft then set lighting power density to 1.0 W/sqft
If climate zone is 5a then set heating efficiency to 0.85
```

Parse them:

```python
from baseline_generator import RuleParser

parser = RuleParser()
with open('my_rules.txt') as f:
    rules = parser.parse_rules_from_text(f.read())
```

### Option 2: Write JSON Rules

Create a JSON file following the schema (see `examples/example_rules.json`):

```json
{
  "version": "1.0",
  "rules": [
    {
      "id": "my_rule_001",
      "name": "My Custom Rule",
      "description": "Description of what this rule does",
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
```

## Creating Building Specifications

Create a YAML or JSON file with your building properties:

```yaml
# my_building.yaml
building_type: office
building_area: 15000  # sqft
climate_zone: "5a"
num_stories: 2
window_to_wall_ratio: 30  # percent
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=baseline_generator
```

## Common Use Cases

### Use Case 1: Quick Baseline Check

```bash
generate_baseline my_building.yaml --verbose
```

### Use Case 2: Compare Multiple Rules Files

```bash
generate_baseline building.yaml --rules rules_v1.json -o baseline_v1.json
generate_baseline building.yaml --rules rules_v2.json -o baseline_v2.json
diff baseline_v1.json baseline_v2.json
```

### Use Case 3: Batch Processing

```python
from baseline_generator import BaselineEngine, RuleSchema
import json
from pathlib import Path

# Load rules once
with open('rules.json') as f:
    schema = RuleSchema.from_dict(json.load(f))

engine = BaselineEngine(schema)

# Process multiple buildings
building_files = Path('buildings').glob('*.json')
for building_file in building_files:
    with open(building_file) as f:
        spec = json.load(f)
    
    baseline = engine.generate_baseline(spec)
    
    output_file = f"baselines/{building_file.stem}_baseline.json"
    with open(output_file, 'w') as f:
        json.dump(baseline, f, indent=2)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the [examples/](examples/) directory
- Check out the [tests/](tests/) for more usage examples
- Create your own synthetic rules (remember: no copyrighted content!)

## Need Help?

- Check the examples in the `examples/` directory
- Run tests to see working code: `pytest tests/test_integration.py -v`
- Review the module docstrings for API documentation

## Important Reminder

⚠️ **NO COPYRIGHTED CONTENT**: This tool is designed to work with synthetic or appropriately licensed rules only. Do not use copyrighted ASHRAE, IECC, or other proprietary building code content without proper authorization.
