"""
Tests for the rules_loader module.

This module contains unit tests for loading and validating rules from YAML files.
"""

import os
import tempfile
import pytest
from pathlib import Path
from typing import List

import yaml

from test_gen.rule_engine.rules_loader import load_rules
from test_gen.rule_engine.models import Rule


class TestRulesLoader:
    """Test cases for the rules_loader module."""
    
    def test_load_valid_single_rule(self):
        """Test loading a single valid rule file."""
        rule_data = {
            'id': 'search_input_basic',
            'description': 'Detects a user typing into a search box',
            'match': {
                'event': {
                    'action': 'input'
                },
                'node': {
                    'tag': 'input',
                    'attributes': {
                        'type': 'search'
                    }
                }
            },
            'confidence': 0.8,
            'variables': {
                'input_value': 'event.value',
                'placeholder': 'node.attributes.placeholder'
            },
            'action_id': 'search_query'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'test_rule.yaml'
            with open(rule_file, 'w') as f:
                yaml.dump(rule_data, f)
            
            rules = load_rules(temp_dir)
            
            assert len(rules) == 1
            rule = rules[0]
            assert isinstance(rule, Rule)
            assert rule.id == 'search_input_basic'
            assert rule.description == 'Detects a user typing into a search box'
            assert rule.confidence == 0.8
            assert rule.action_id == 'search_query'
            assert rule.match == rule_data['match']
            assert rule.variables == rule_data['variables']
    
    def test_load_multiple_rules(self):
        """Test loading multiple rule files from a directory."""
        rule1 = {
            'id': 'rule1',
            'match': {'event': {'action': 'click'}},
            'confidence': 0.9,
            'variables': {'target': 'node.id'},
            'action_id': 'button_click'
        }
        
        rule2 = {
            'id': 'rule2',
            'description': 'Second rule',
            'match': {'event': {'action': 'input'}},
            'confidence': 0.7,
            'variables': {'value': 'event.value'},
            'action_id': 'text_input'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create two rule files
            with open(Path(temp_dir) / 'rule1.yaml', 'w') as f:
                yaml.dump(rule1, f)
            with open(Path(temp_dir) / 'rule2.yml', 'w') as f:
                yaml.dump(rule2, f)
            
            rules = load_rules(temp_dir)
            
            assert len(rules) == 2
            rule_ids = [rule.id for rule in rules]
            assert 'rule1' in rule_ids
            assert 'rule2' in rule_ids
    
    def test_load_rule_without_description(self):
        """Test loading a rule without optional description field."""
        rule_data = {
            'id': 'minimal_rule',
            'match': {'event': {'action': 'click'}},
            'confidence': 0.5,
            'variables': {},
            'action_id': 'click_action'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'minimal.yaml'
            with open(rule_file, 'w') as f:
                yaml.dump(rule_data, f)
            
            rules = load_rules(temp_dir)
            
            assert len(rules) == 1
            rule = rules[0]
            assert rule.id == 'minimal_rule'
            assert rule.description is None
    
    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise ValueError."""
        incomplete_rule = {
            'id': 'incomplete_rule',
            'match': {'event': {'action': 'click'}},
            'confidence': 0.8
            # Missing 'variables' and 'action_id'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'incomplete.yaml'
            with open(rule_file, 'w') as f:
                yaml.dump(incomplete_rule, f)
            
            with pytest.raises(ValueError) as exc_info:
                load_rules(temp_dir)
            
            assert "missing required fields" in str(exc_info.value)
            assert "variables" in str(exc_info.value)
            assert "action_id" in str(exc_info.value)
    
    def test_invalid_confidence_value_raises_error(self):
        """Test that invalid confidence values raise ValueError."""
        rule_with_invalid_confidence = {
            'id': 'invalid_confidence',
            'match': {'event': {'action': 'click'}},
            'confidence': 1.5,  # Invalid: > 1
            'variables': {},
            'action_id': 'click_action'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'invalid.yaml'
            with open(rule_file, 'w') as f:
                yaml.dump(rule_with_invalid_confidence, f)
            
            with pytest.raises(ValueError) as exc_info:
                load_rules(temp_dir)
            
            assert "confidence" in str(exc_info.value)
            assert "between 0 and 1" in str(exc_info.value)
    
    def test_invalid_field_types_raise_error(self):
        """Test that invalid field types raise ValueError."""
        rule_with_wrong_types = {
            'id': 123,  # Should be string
            'match': "not a dict",  # Should be dict
            'confidence': 0.8,
            'variables': "not a dict",  # Should be dict
            'action_id': ['not', 'a', 'string']  # Should be string
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'wrong_types.yaml'
            with open(rule_file, 'w') as f:
                yaml.dump(rule_with_wrong_types, f)
            
            with pytest.raises(ValueError) as exc_info:
                load_rules(temp_dir)
            
            assert "must be a string" in str(exc_info.value)
    
    def test_malformed_yaml_raises_error(self):
        """Test that malformed YAML files raise YAMLError."""
        malformed_yaml = """
        id: test_rule
        match:
          event:
            action: click
          invalid_yaml: [unclosed bracket
        """
        
        with tempfile.TemporaryDirectory() as temp_dir:
            rule_file = Path(temp_dir) / 'malformed.yaml'
            with open(rule_file, 'w') as f:
                f.write(malformed_yaml)
            
            with pytest.raises(yaml.YAMLError):
                load_rules(temp_dir)
    
    def test_nonexistent_directory_raises_error(self):
        """Test that nonexistent directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_rules('/nonexistent/directory')
    
    def test_file_path_instead_of_directory_raises_error(self):
        """Test that passing a file path instead of directory raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix='.yaml') as temp_file:
            with pytest.raises(ValueError) as exc_info:
                load_rules(temp_file.name)
            
            assert "not a directory" in str(exc_info.value)
    
    def test_empty_directory_returns_empty_list(self):
        """Test that empty directory returns empty list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules = load_rules(temp_dir)
            assert rules == []
    
    def test_directory_with_non_yaml_files_ignores_them(self):
        """Test that non-YAML files are ignored."""
        rule_data = {
            'id': 'valid_rule',
            'match': {'event': {'action': 'click'}},
            'confidence': 0.8,
            'variables': {},
            'action_id': 'click_action'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a valid YAML file
            with open(Path(temp_dir) / 'valid.yaml', 'w') as f:
                yaml.dump(rule_data, f)
            
            # Create non-YAML files that should be ignored
            with open(Path(temp_dir) / 'readme.txt', 'w') as f:
                f.write('This is not a rule file')
            with open(Path(temp_dir) / 'config.json', 'w') as f:
                f.write('{"not": "a rule"}')
            
            rules = load_rules(temp_dir)
            
            assert len(rules) == 1
            assert rules[0].id == 'valid_rule'
    
    def test_empty_yaml_file_is_skipped(self):
        """Test that empty YAML files are skipped."""
        rule_data = {
            'id': 'valid_rule',
            'match': {'event': {'action': 'click'}},
            'confidence': 0.8,
            'variables': {},
            'action_id': 'click_action'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a valid rule file
            with open(Path(temp_dir) / 'valid.yaml', 'w') as f:
                yaml.dump(rule_data, f)
            
            # Create an empty YAML file
            with open(Path(temp_dir) / 'empty.yaml', 'w') as f:
                pass  # Empty file
            
            rules = load_rules(temp_dir)
            
            assert len(rules) == 1
            assert rules[0].id == 'valid_rule'