# Baseline Model Auto-Generation

A Python framework for converting regulatory-style building-energy rules into structured JSON logic and generating baseline model specifications.

## ⚠️ Important: No Copyrighted Content

**This project does NOT include any copyrighted ASHRAE 90.1, IECC, or other proprietary building energy code content.** All examples and rules are synthetic and created for demonstration purposes only. Users are responsible for creating their own rule sets based on publicly available or appropriately licensed sources.

## Features

- **Text-to-JSON Parser**: Convert natural language building energy rules into structured JSON format
- **Rule Schema**: Well-defined schema for representing building energy compliance rules
- **Baseline Rule Engine**: Evaluate building specifications against rules and generate baseline models
- **CLI Tool**: Command-line interface for easy baseline generation
- **Extensible**: Easy to add new rules and customize behavior

## Project Structure

```
.
├── src/baseline_generator/    # Main package
│   ├── __init__.py           # Package initialization
│   ├── schema.py             # Rule schema definitions
│   ├── parser.py             # Text-to-JSON parser
│   ├── engine.py             # Baseline rule engine
│   └── cli.py                # Command-line interface
├── examples/                  # Synthetic examples
│   ├── example_rules.json    # Example rules in JSON
│   ├── example_rules_text.txt # Example rules in text
│   └── example_building_spec.yaml # Sample building spec
├── tests/                     # Test suite
│   ├── test_schema.py
│   ├── test_parser.py
│   └── test_engine.py
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Icy-Mint/Baseline-Model-Auto-Generation-.git
cd Baseline-Model-Auto-Generation-

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.8 or higher
- PyYAML 6.0 or higher

## Usage

### Command Line Interface

The `generate_baseline` command takes a building specification file and generates a baseline model:

```bash
# Basic usage
generate_baseline examples/example_building_spec.yaml

# Save output to file
generate_baseline examples/example_building_spec.yaml --output baseline.json

# Use custom rules
generate_baseline input.yaml --rules my_rules.json --output baseline.json

# Output in YAML format
generate_baseline input.yaml --format yaml --output baseline.yaml

# Verbose mode
generate_baseline input.yaml --verbose
```

### Python API

```python
from baseline_generator import RuleSchema, BaselineEngine, RuleParser

# Load rules from JSON file
with open('rules.json') as f:
    import json
    rules_data = json.load(f)
    
rule_schema = RuleSchema.from_dict(rules_data)

# Create engine
engine = BaselineEngine(rule_schema)

# Define building specification
building_spec = {
    "building_type": "office",
    "building_area": 15000,
    "climate_zone": "5a",
    "num_stories": 2
}

# Generate baseline
baseline = engine.generate_baseline(building_spec)
print(baseline)

# Get applicable rules
applicable_rules = engine.get_applicable_rules(building_spec)
for rule in applicable_rules:
    print(f"Rule {rule.id}: {rule.name}")
```

### Parsing Text Rules

```python
from baseline_generator import RuleParser

parser = RuleParser()

# Parse single rule
text = "If building type is office and building area is less than 25000 sqft then set lighting power density to 1.0 W/sqft"
rule = parser.parse_rule_text(text, category="lighting")

# Parse multiple rules
rules_text = """
If building type is office then set lighting to 1.0
If building type is retail then set lighting to 1.5
"""
rules = parser.parse_rules_from_text(rules_text, category="lighting")
```

## Rule Schema

Rules are defined using a structured JSON schema:

```json
{
  "version": "1.0",
  "rules": [
    {
      "id": "rule_001",
      "name": "Small Office Lighting",
      "description": "Lighting power density for small office buildings",
      "category": "lighting",
      "priority": 10,
      "conditions": {
        "operator": "and",
        "conditions": [
          {
            "field": "building_type",
            "operator": "equals",
            "value": "office"
          },
          {
            "field": "building_area",
            "operator": "less_than",
            "value": 25000,
            "unit": "sqft"
          }
        ]
      },
      "actions": [
        {
          "action_type": "set_value",
          "target": "lighting_power_density",
          "value": 1.0,
          "parameters": {
            "unit": "W/sqft"
          }
        }
      ]
    }
  ]
}
```

### Supported Operators

**Comparison Operators:**
- `equals` / `not_equals`
- `greater_than` / `less_than`
- `greater_than_or_equal` / `less_than_or_equal`
- `in` / `not_in`

**Logical Operators:**
- `and` - All conditions must be met
- `or` - At least one condition must be met
- `not` - Negation

### Action Types

- `set_value`: Set a property to a specific value
- `apply_method`: Reference a calculation method
- `reference_table`: Reference a lookup table
- `evaluate`: Custom evaluation action

## Building Specification Format

Input building specifications can be provided in YAML or JSON:

```yaml
# example_building_spec.yaml
building_type: office
building_area: 15000  # sqft
climate_zone: "5a"
num_stories: 2
window_to_wall_ratio: 30  # percent
construction_type: steel_frame
```

## Examples

The `examples/` directory contains synthetic examples:

- `example_rules.json` - Complete rule set in JSON format
- `example_rules_text.txt` - Rules in natural language
- `example_building_spec.yaml` - Sample building specification
- `README.md` - Documentation about examples

**Remember**: All examples are synthetic and for demonstration only. They do not represent actual building codes or standards.

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=baseline_generator --cov-report=html
```

## Development

### Project Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

### Adding New Rules

1. Define rules in JSON format following the schema
2. Load them into the engine
3. Test with sample building specifications

### Extending the Parser

The parser uses pattern matching to extract rules from text. To improve parsing:

1. Add new patterns to `PROPERTY_PATTERNS`, `OPERATOR_PATTERNS`, or `UNIT_PATTERNS` in `parser.py`
2. Implement custom parsing logic for complex rule structures
3. Test with diverse rule formats

## Contributing

Contributions are welcome! Please ensure:

1. No copyrighted content is included
2. All examples are clearly marked as synthetic
3. Tests pass for new features
4. Code follows existing style conventions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided for educational and demonstration purposes only. It does not constitute professional engineering advice or code compliance guidance. Users are responsible for ensuring their building designs comply with applicable codes and standards.

**No warranty is provided regarding the accuracy, completeness, or suitability of this software for any particular purpose.**
