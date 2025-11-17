"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path

import pytest

from baseline_generator.cli import load_yaml_file, load_json_file, save_output


class TestCLI:
    """Tests for CLI functionality."""
    
    def test_load_json_file(self, tmp_path):
        """Test loading JSON file."""
        data = {"test": "data", "number": 42}
        json_file = tmp_path / "test.json"
        
        with open(json_file, 'w') as f:
            json.dump(data, f)
        
        loaded = load_json_file(str(json_file))
        assert loaded == data
    
    def test_save_output_json(self, tmp_path):
        """Test saving output as JSON."""
        data = {"result": "success", "value": 123}
        output_file = tmp_path / "output.json"
        
        save_output(data, str(output_file), "json")
        
        with open(output_file) as f:
            loaded = json.load(f)
        
        assert loaded == data
    
    def test_save_output_yaml(self, tmp_path):
        """Test saving output as YAML."""
        try:
            import yaml
            has_yaml = True
        except ImportError:
            has_yaml = False
        
        data = {"result": "success", "value": 123}
        output_file = tmp_path / "output.yaml"
        
        save_output(data, str(output_file), "yaml")
        
        # Should save even if yaml not available (falls back to JSON)
        with open(output_file) as f:
            content = f.read()
        
        assert "result" in content
        assert "success" in content
