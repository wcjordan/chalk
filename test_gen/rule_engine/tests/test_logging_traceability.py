"""
Tests for logging and rule match traceability functionality.

This module tests that proper logging is emitted during rule evaluation,
variable extraction, and chunk processing, and that verbosity flags work correctly.
"""

import logging
import pytest
from unittest.mock import Mock

from feature_extraction.models import UserInteraction, UINode
from test_gen.rule_engine.models import Rule, DetectedAction
from test_gen.rule_engine.matcher import (
    rule_matches_event_node,
    apply_rule_to_event_and_node,
    detect_actions_in_chunk,
)
from test_gen.rule_engine.variable_resolver import extract_variables


@pytest.fixture
def sample_rule():
    """Create a sample rule for testing."""
    return Rule(
        id="test_rule",
        description="Test rule for logging",
        match={
            "event": {"action": "input"},
            "node": {"tag": "input", "attributes": {"type": "text"}}
        },
        confidence=0.8,
        variables={"input_value": "event.value", "placeholder": "node.attributes.placeholder"},
        action_id="test_action"
    )


@pytest.fixture
def sample_event():
    """Create a sample UserInteraction for testing."""
    return UserInteraction(
        action="input",
        timestamp=1234567890,
        target_id="input_1",
        value="test input"
    )


@pytest.fixture
def sample_node():
    """Create a sample UINode for testing."""
    return UINode(
        id="input_1",
        tag="input",
        text="",
        attributes={"type": "text", "placeholder": "Enter text..."}
    )


@pytest.fixture
def mismatched_node():
    """Create a UINode that won't match the sample rule."""
    return UINode(
        id="button_1",
        tag="button",
        text="Click me",
        attributes={"type": "submit"}
    )


@pytest.fixture
def sample_chunk():
    """Create a sample chunk for testing."""
    return Mock(
        chunk_id="test_chunk_123",
        features=Mock(
            interactions=[
                UserInteraction(
                    action="input",
                    timestamp=1234567890,
                    target_id="input_1",
                    value="test input"
                )
            ],
            ui_nodes={
                "input_1": UINode(
                    id="input_1",
                    tag="input",
                    text="",
                    attributes={"type": "text", "placeholder": "Enter text..."}
                )
            }
        )
    )


class TestRuleMatchLogging:
    """Test logging during rule matching operations."""

    def test_successful_match_logs_info(self, caplog, sample_rule, sample_event, sample_node):
        """Test that successful rule matches log INFO messages with rule details."""
        with caplog.at_level(logging.INFO, logger="test_gen.rule_engine"):
            result = apply_rule_to_event_and_node(sample_rule, sample_event, sample_node, 0)
        
        assert result is not None
        assert result.action_id == "test_action"
        
        # Check that INFO log was emitted for the match
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        assert len(info_logs) >= 1
        
        log_message = info_logs[0].message
        assert "test_rule" in log_message
        assert "test_action" in log_message
        assert "event_index=0" in log_message
        assert "timestamp=1234567890" in log_message
        assert "variables=" in log_message

    def test_rule_evaluation_debug_logging(self, caplog, sample_rule, sample_event, sample_node):
        """Test that rule evaluation emits DEBUG logs with evaluation details."""
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            rule_matches_event_node(sample_rule, sample_event, sample_node)
        
        # Check that DEBUG log was emitted for rule evaluation start
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        assert len(debug_logs) >= 1
        
        log_message = debug_logs[0].message
        assert "Evaluating rule 'test_rule'" in log_message
        assert "event.action='input'" in log_message
        assert "node.tag='input'" in log_message
        assert "node.id='input_1'" in log_message

    def test_action_mismatch_debug_logging(self, caplog, sample_rule, sample_node):
        """Test that action mismatches are logged at DEBUG level."""
        # Create an event with wrong action
        wrong_event = UserInteraction(
            action="click",
            timestamp=1234567890,
            target_id="input_1",
            value="test"
        )
        
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            result = rule_matches_event_node(sample_rule, wrong_event, sample_node)
        
        assert result is False
        
        # Check that DEBUG log was emitted for action mismatch
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        mismatch_logs = [log for log in debug_logs if "action mismatch" in log.message]
        assert len(mismatch_logs) >= 1
        
        log_message = mismatch_logs[0].message
        assert "expected: input" in log_message
        assert "got: click" in log_message

    def test_tag_mismatch_debug_logging(self, caplog, sample_rule, sample_event, mismatched_node):
        """Test that tag mismatches are logged at DEBUG level."""
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            result = rule_matches_event_node(sample_rule, sample_event, mismatched_node)
        
        assert result is False
        
        # Check that DEBUG log was emitted for tag mismatch
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        mismatch_logs = [log for log in debug_logs if "tag mismatch" in log.message]
        assert len(mismatch_logs) >= 1
        
        log_message = mismatch_logs[0].message
        assert "expected: input" in log_message
        assert "got: button" in log_message

    def test_missing_attributes_debug_logging(self, caplog, sample_event):
        """Test that missing attributes are logged at DEBUG level."""
        # Create a rule that requires an attribute not present on the node
        rule = Rule(
            id="missing_attr_rule",
            description="Rule requiring missing attribute",
            match={
                "event": {"action": "input"},
                "node": {"tag": "input", "attributes": {"required_attr": "value"}}
            },
            confidence=0.8,
            variables={},
            action_id="test_action"
        )
        
        # Create a node without the required attribute
        node = UINode(
            id="input_1",
            tag="input",
            text="",
            attributes={"type": "text"}  # missing 'required_attr'
        )
        
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            result = rule_matches_event_node(rule, sample_event, node)
        
        assert result is False
        
        # Check that DEBUG log was emitted for missing attributes
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        missing_logs = [log for log in debug_logs if "Missing attributes" in log.message]
        assert len(missing_logs) >= 1
        
        log_message = missing_logs[0].message
        assert "required_attr" in log_message


class TestVariableExtractionLogging:
    """Test logging during variable extraction."""

    def test_variable_extraction_failure_debug_logging(self, caplog, sample_event, sample_node):
        """Test that variable extraction failures are logged at DEBUG level."""
        variable_map = {
            "existing_value": "event.value",
            "missing_attribute": "node.attributes.nonexistent",
            "invalid_path": "node.invalid.path"
        }
        
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            result = extract_variables(variable_map, sample_event, sample_node)
        
        assert result["existing_value"] == "test input"
        assert result["missing_attribute"] is None
        assert result["invalid_path"] is None
        
        # Check that DEBUG logs were emitted for extraction failures
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        failure_logs = [log for log in debug_logs if "Variable extraction failed" in log.message]
        assert len(failure_logs) >= 2  # Should have failures for missing_attribute and invalid_path
        
        # Check specific failure messages
        failure_messages = [log.message for log in failure_logs]
        assert any("missing_attribute" in msg and "node.attributes.nonexistent" in msg for msg in failure_messages)
        assert any("invalid_path" in msg and "node.invalid.path" in msg for msg in failure_messages)


class TestChunkProcessingLogging:
    """Test logging during full chunk processing."""

    def test_chunk_processing_info_logging(self, caplog, sample_chunk, sample_rule):
        """Test that chunk processing emits INFO logs with summary statistics."""
        with caplog.at_level(logging.INFO, logger="test_gen.rule_engine"):
            results = detect_actions_in_chunk(sample_chunk, [sample_rule])
        
        assert len(results) == 1  # Should find one match
        
        # Check that INFO log was emitted for chunk processing summary
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        summary_logs = [log for log in info_logs if "Chunk processing complete" in log.message]
        assert len(summary_logs) >= 1
        
        log_message = summary_logs[0].message
        assert "1 rules evaluated" in log_message
        assert "1 matches found" in log_message
        assert "1 distinct rules matched" in log_message

    def test_chunk_processing_debug_logging(self, caplog, sample_chunk, sample_rule):
        """Test that chunk processing emits DEBUG logs about interactions processed."""
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            detect_actions_in_chunk(sample_chunk, [sample_rule])
        
        # Check that DEBUG log was emitted for interaction count
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        interaction_logs = [log for log in debug_logs if "Processing" in log.message and "interactions" in log.message]
        assert len(interaction_logs) >= 1
        
        log_message = interaction_logs[0].message
        assert "Processing 1 interactions in chunk" in log_message


class TestVerbosityToggling:
    """Test that verbosity flags work correctly for controlling log levels."""

    def test_default_warning_level_suppresses_info_debug(self, caplog, sample_rule, sample_event, sample_node):
        """Test that with no verbosity flags, only WARNING+ logs are shown."""
        # Simulate default logging level (WARNING)
        with caplog.at_level(logging.WARNING, logger="test_gen.rule_engine"):
            apply_rule_to_event_and_node(sample_rule, sample_event, sample_node, 0)
        
        # Should have no INFO or DEBUG logs
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        assert len(info_logs) == 0
        assert len(debug_logs) == 0

    def test_verbose_enables_info_logs(self, caplog, sample_rule, sample_event, sample_node):
        """Test that --verbose flag enables INFO level logs."""
        # Simulate verbose mode (INFO level)
        with caplog.at_level(logging.INFO, logger="test_gen.rule_engine"):
            apply_rule_to_event_and_node(sample_rule, sample_event, sample_node, 0)
        
        # Should have INFO logs but still filter DEBUG
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        assert len(info_logs) >= 1  # Should have match INFO log
        # Note: DEBUG logs might still appear if we capture at INFO level

    def test_trace_match_enables_debug_logs(self, caplog, sample_rule, sample_event, sample_node):
        """Test that --trace-match flag enables DEBUG level logs."""
        # Simulate trace-match mode (DEBUG level)
        with caplog.at_level(logging.DEBUG, logger="test_gen.rule_engine"):
            apply_rule_to_event_and_node(sample_rule, sample_event, sample_node, 0)
        
        # Should have both INFO and DEBUG logs
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        debug_logs = [record for record in caplog.records if record.levelno == logging.DEBUG]
        assert len(info_logs) >= 1  # Should have match INFO log
        assert len(debug_logs) >= 1  # Should have evaluation DEBUG log

    def test_variable_truncation_in_logs(self, caplog, sample_event, sample_node):
        """Test that large variable values are truncated in logs."""
        # Create a rule with a variable that will extract a long value
        long_value_event = UserInteraction(
            action="input",
            timestamp=1234567890,
            target_id="input_1",
            value="a" * 100  # 100 character string
        )
        
        rule = Rule(
            id="long_value_rule",
            description="Rule that extracts long values",
            match={
                "event": {"action": "input"},
                "node": {"tag": "input"}
            },
            confidence=0.8,
            variables={"long_value": "event.value"},
            action_id="test_action"
        )
        
        with caplog.at_level(logging.INFO, logger="test_gen.rule_engine"):
            apply_rule_to_event_and_node(rule, long_value_event, sample_node, 0)
        
        # Check that the variable value was truncated in the log
        info_logs = [record for record in caplog.records if record.levelno == logging.INFO]
        match_logs = [log for log in info_logs if "matched" in log.message]
        assert len(match_logs) >= 1
        
        log_message = match_logs[0].message
        assert "..." in log_message  # Should contain ellipsis for truncated value
        assert "a" * 100 not in log_message  # Should not contain the full long value