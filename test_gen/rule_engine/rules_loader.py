"""
Rule loader module for loading YAML rule files from disk.

This module provides functionality to load and validate rules from YAML files,
converting them into Rule objects for use in the rule-based action detection system.
"""

import os
from pathlib import Path
from typing import List, Union, Dict, Any

import yaml

from .models import Rule


def load_rules(directory: Union[str, Path]) -> List[Rule]:
    """
    Load and validate rules from YAML files in the specified directory.
    
    Args:
        directory: Path to the directory containing rule YAML files
        
    Returns:
        List of Rule objects parsed from the YAML files
        
    Raises:
        ValueError: If any rule is missing required fields or has invalid structure
        FileNotFoundError: If the directory doesn't exist
        yaml.YAMLError: If YAML files are malformed
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        raise FileNotFoundError(f"Rules directory does not exist: {directory}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    rules = []
    yaml_files = list(directory_path.glob("*.yaml")) + list(directory_path.glob("*.yml"))
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                rule_data = yaml.safe_load(file)
                
            if rule_data is None:
                continue  # Skip empty files
                
            rule = _parse_rule(rule_data, yaml_file.name)
            rules.append(rule)
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {yaml_file.name}: {e}")
        except Exception as e:
            raise ValueError(f"Error processing rule file {yaml_file.name}: {e}")
    
    return rules


def _parse_rule(rule_data: Dict[str, Any], filename: str) -> Rule:
    """
    Parse rule data from YAML into a Rule object.
    
    Args:
        rule_data: Dictionary containing rule data from YAML
        filename: Name of the file being parsed (for error messages)
        
    Returns:
        Rule object
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = ['id', 'match', 'confidence', 'variables', 'action_id']
    
    # Check for required fields
    missing_fields = [field for field in required_fields if field not in rule_data]
    if missing_fields:
        raise ValueError(f"Rule in {filename} missing required fields: {missing_fields}")
    
    # Validate field types
    if not isinstance(rule_data['id'], str):
        raise ValueError(f"Rule in {filename}: 'id' must be a string")
    
    if not isinstance(rule_data['match'], dict):
        raise ValueError(f"Rule in {filename}: 'match' must be a dictionary")
    
    if not isinstance(rule_data['confidence'], (int, float)) or not (0 <= rule_data['confidence'] <= 1):
        raise ValueError(f"Rule in {filename}: 'confidence' must be a number between 0 and 1")
    
    if not isinstance(rule_data['variables'], dict):
        raise ValueError(f"Rule in {filename}: 'variables' must be a dictionary")
    
    if not isinstance(rule_data['action_id'], str):
        raise ValueError(f"Rule in {filename}: 'action_id' must be a string")
    
    # Optional description field
    description = rule_data.get('description')
    if description is not None and not isinstance(description, str):
        raise ValueError(f"Rule in {filename}: 'description' must be a string")
    
    return Rule(
        id=rule_data['id'],
        description=description,
        match=rule_data['match'],
        confidence=float(rule_data['confidence']),
        variables=rule_data['variables'],
        action_id=rule_data['action_id']
    )