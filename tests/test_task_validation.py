"""
Tests for OOS Task System validation.

Comprehensive test suite for TaskValidator including field validation,
business rules, and constraint checking.
"""

import pytest
from datetime import datetime, timedelta

from src.oos_task_system.models import Task, TaskStatus, TaskPriority
from src.oos_task_system.validation import TaskValidator, ValidationError, ValidationResult


class TestValidationResult:
    """Test suite for ValidationResult."""

    def test_validation_result_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Test adding validation errors."""
        result = ValidationResult()

        result.add_error('title', 'Title is required')

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field == 'title'
        assert result.errors[0].message == 'Title is required'

    def test_add_warning(self):
        """Test adding validation warnings."""
        result = ValidationResult()

        result.add_warning('This is a warning')

        assert result.is_valid is True  # Warnings don't affect validity
        assert len(result.warnings) == 1
        assert result.warnings[0] == 'This is a warning'

    def test_get_error_summary(self):
        """Test error summary grouping."""
        result = ValidationResult()

        result.add_error('title', 'Title is too short')
        result.add_error('title', 'Title has invalid characters')
        result.add_error('tags', 'Too many tags')

        summary = result.get_error_summary()

        assert 'title' in summary
        assert 'tags' in summary
        assert len(summary['title']) == 2
        assert len(summary['tags']) == 1
        assert 'Title is too short' in summary['title']
        assert 'Too many tags' in summary['tags']


class TestTaskValidator:
    """Test suite for TaskValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TaskValidator()

    def test_validate_task_minimal_valid(self):
        """Test validation of minimal valid task."""
        task = Task(title="Valid Task")

        result = self.validator.validate_task(task)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_title_empty(self):
        """Test title validation with empty title."""
        result = ValidationResult()
        self.validator._validate_title("", result, strict=True)

        assert result.is_valid is False
        assert any('empty' in error.message for error in result.errors)

    def test_validate_title_too_long(self):
        """Test title validation with overly long title."""
        long_title = "x" * (TaskValidator.MAX_TITLE_LENGTH + 1)
        result = ValidationResult()
        self.validator._validate_title(long_title, result, strict=True)

        assert result.is_valid is False
        assert any('exceed' in error.message for error in result.errors)

    def test_validate_title_whitespace_issues(self):
        """Test title validation with whitespace issues."""
        result = ValidationResult()
        self.validator._validate_title("  Title with spaces  ", result, strict=True)

        # Should have warnings about whitespace in strict mode
        assert len(result.warnings) > 0

        # Test multiple spaces
        result2 = ValidationResult()
        self.validator._validate_title("Title  with  multiple  spaces", result2, strict=True)
        assert len(result2.warnings) > 0

    def test_validate_description_too_long(self):
        """Test description validation with overly long description."""
        long_desc = "x" * (TaskValidator.MAX_DESCRIPTION_LENGTH + 1)
        result = ValidationResult()
        self.validator._validate_description(long_desc, result, strict=True)

        assert result.is_valid is False
        assert any('exceed' in error.message for error in result.errors)

    def test_validate_id_invalid_characters(self):
        """Test ID validation with invalid characters."""
        result = ValidationResult()
        self.validator._validate_id("task@#$", result, strict=True)

        assert result.is_valid is False
        assert any('invalid characters' in error.message for error in result.errors)

    def test_validate_id_too_long(self):
        """Test ID validation with overly long ID."""
        long_id = "x" * 51
        result = ValidationResult()
        self.validator._validate_id(long_id, result, strict=True)

        assert result.is_valid is False

    def test_validate_tags_invalid_type(self):
        """Test tags validation with invalid type."""
        result = ValidationResult()
        self.validator._validate_tags("not-a-list", result, strict=True)

        assert result.is_valid is False
        assert any('must be a list' in error.message for error in result.errors)

    def test_validate_tags_too_many(self):
        """Test tags validation with too many tags."""
        too_many_tags = [f"tag{i}" for i in range(TaskValidator.MAX_TAGS_COUNT + 1)]
        result = ValidationResult()
        self.validator._validate_tags(too_many_tags, result, strict=True)

        assert result.is_valid is False
        assert any('more than' in error.message for error in result.errors)

    def test_validate_tags_invalid_characters(self):
        """Test tags validation with invalid characters in strict mode."""
        result = ValidationResult()
        self.validator._validate_tags(["valid-tag", "invalid tag!", "another_valid"], result, strict=True)

        assert result.is_valid is False
        assert any('invalid characters' in error.message for error in result.errors)

    def test_validate_tags_duplicates(self):
        """Test tags validation with duplicate tags."""
        result = ValidationResult()
        self.validator._validate_tags(["tag1", "tag2", "TAG1"], result, strict=True)

        # Should have warning about duplicate (case-insensitive)
        assert any('Duplicate tag' in warning for warning in result.warnings)

    def test_validate_dependencies_invalid_type(self):
        """Test dependencies validation with invalid type."""
        result = ValidationResult()
        self.validator._validate_dependencies("not-a-list", result, strict=True)

        assert result.is_valid is False
        assert any('must be a list' in error.message for error in result.errors)

    def test_validate_dependencies_too_many(self):
        """Test dependencies validation with too many dependencies."""
        too_many_deps = [f"dep{i}" for i in range(TaskValidator.MAX_DEPENDENCIES + 1)]
        result = ValidationResult()
        self.validator._validate_dependencies(too_many_deps, result, strict=True)

        assert result.is_valid is False

    def test_validate_assignee_too_long(self):
        """Test assignee validation with overly long assignee."""
        long_assignee = "x" * (TaskValidator.MAX_ASSIGNEE_LENGTH + 1)
        result = ValidationResult()
        self.validator._validate_assignee(long_assignee, result, strict=True)

        assert result.is_valid is False

    def test_validate_assignee_invalid_characters(self):
        """Test assignee validation with invalid characters in strict mode."""
        result = ValidationResult()
        self.validator._validate_assignee("user@#$%", result, strict=True)

        assert result.is_valid is False

    def test_validate_hours_negative(self):
        """Test hours validation with negative values."""
        result = ValidationResult()
        self.validator._validate_hours(-5.0, -2.0, result)

        assert result.is_valid is False
        assert len([e for e in result.errors if 'negative' in e.message]) == 2

    def test_validate_hours_too_large(self):
        """Test hours validation with overly large values."""
        result = ValidationResult()
        self.validator._validate_hours(
            TaskValidator.MAX_ESTIMATED_HOURS + 1,
            TaskValidator.MAX_ACTUAL_HOURS + 1,
            result
        )

        assert result.is_valid is False
        assert len([e for e in result.errors if 'exceed' in e.message]) == 2

    def test_validate_hours_actual_much_larger(self):
        """Test hours validation when actual is much larger than estimated."""
        result = ValidationResult()
        self.validator._validate_hours(2.0, 10.0, result)  # 5x estimated

        # Should have warning
        assert len(result.warnings) > 0
        assert any('exceed' in warning for warning in result.warnings)

    def test_validate_dates_invalid_types(self):
        """Test date validation with invalid types."""
        result = ValidationResult()
        self.validator._validate_dates("not-a-date", datetime.now(), None, None, result)

        assert result.is_valid is False
        assert any('datetime' in error.message for error in result.errors)

    def test_validate_dates_updated_before_created(self):
        """Test date validation when updated is before created."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        result = ValidationResult()
        self.validator._validate_dates(now, yesterday, None, None, result)

        assert result.is_valid is False
        assert any('before created' in error.message for error in result.errors)

    def test_validate_dates_completed_before_created(self):
        """Test date validation when completed is before created."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)

        result = ValidationResult()
        self.validator._validate_dates(now, now, yesterday, None, result)

        assert result.is_valid is False

    def test_validate_dates_future_created(self):
        """Test date validation with future created date."""
        future = datetime.now() + timedelta(hours=1)

        result = ValidationResult()
        self.validator._validate_dates(future, future, None, None, result)

        # Should have warning about future date
        assert len(result.warnings) > 0

    def test_validate_context_invalid_type(self):
        """Test context validation with invalid type."""
        result = ValidationResult()
        self.validator._validate_context("not-a-dict", result, strict=True)

        assert result.is_valid is False
        assert any('dictionary' in error.message for error in result.errors)

    def test_validate_context_non_serializable(self):
        """Test context validation with non-serializable data."""
        class NonSerializable:
            pass

        context = {"bad_data": NonSerializable()}
        result = ValidationResult()
        self.validator._validate_context(context, result, strict=True)

        assert result.is_valid is False
        assert any('serializable' in error.message for error in result.errors)

    def test_validate_business_rules_completed_without_timestamp(self):
        """Test business rule: completed task should have timestamp."""
        task = Task(title="Test", status=TaskStatus.DONE, completed_at=None)

        result = self.validator.validate_task(task)

        # Should have warning
        assert len(result.warnings) > 0
        assert any('completion timestamp' in warning for warning in result.warnings)

    def test_validate_business_rules_non_completed_with_timestamp(self):
        """Test business rule: non-completed task should not have timestamp."""
        task = Task(title="Test", status=TaskStatus.TODO, completed_at=datetime.now())

        result = self.validator.validate_task(task)

        # Should have warning
        assert len(result.warnings) > 0

    def test_validate_business_rules_actual_hours_without_progress(self):
        """Test business rule: actual hours without progress."""
        task = Task(title="Test", status=TaskStatus.TODO, actual_hours=5.0)

        result = self.validator.validate_task(task)

        # Should have warning
        assert len(result.warnings) > 0

    def test_validate_status_transition_invalid(self):
        """Test status transition validation."""
        result = ValidationResult()
        self.validator._validate_status_transition('done', TaskStatus.TODO, result)

        # Should have warning about invalid transition
        assert len(result.warnings) > 0

    def test_validate_field_individual(self):
        """Test validating individual fields."""
        # Test valid field
        result = self.validator.validate_field('title', 'Valid Title')
        assert result.is_valid is True

        # Test invalid field
        result = self.validator.validate_field('title', '')
        assert result.is_valid is False

        # Test unknown field
        result = self.validator.validate_field('unknown_field', 'value')
        assert len(result.warnings) > 0

    def test_validate_complex_task(self):
        """Test validation of complex task with multiple issues."""
        task = Task(
            title="",  # Invalid: empty
            description="x" * 6000,  # Invalid: too long
            tags=["valid", "invalid tag!"],  # Mixed valid/invalid
            depends_on=["dep1"] * 3,  # Duplicates
            assignee="user@#$",  # Invalid characters
            estimated_hours=-1,  # Invalid: negative
            actual_hours=1000000,  # Invalid: too large
        )

        result = self.validator.validate_task(task, strict=True)

        assert result.is_valid is False
        assert len(result.errors) >= 5  # Multiple validation errors

        # Check specific error types
        error_fields = [error.field for error in result.errors]
        assert 'title' in error_fields
        assert 'description' in error_fields
        assert 'assignee' in error_fields
        assert 'estimated_hours' in error_fields
        assert 'actual_hours' in error_fields

    def test_get_field_constraints(self):
        """Test getting field validation constraints."""
        constraints = self.validator.get_field_constraints()

        assert 'title' in constraints
        assert 'tags' in constraints
        assert 'estimated_hours' in constraints

        # Check specific constraints
        title_constraints = constraints['title']
        assert title_constraints['required'] is True
        assert title_constraints['max_length'] == TaskValidator.MAX_TITLE_LENGTH

        tags_constraints = constraints['tags']
        assert tags_constraints['max_count'] == TaskValidator.MAX_TAGS_COUNT

    def test_strict_vs_non_strict_validation(self):
        """Test difference between strict and non-strict validation."""
        task = Task(
            title="  Title with spaces  ",
            tags=["tag with spaces"],
            assignee="user@domain"
        )

        # Non-strict should be more lenient
        result_non_strict = self.validator.validate_task(task, strict=False)

        # Strict should catch more issues
        result_strict = self.validator.validate_task(task, strict=True)

        # Strict mode should have more warnings/errors
        assert len(result_strict.warnings) >= len(result_non_strict.warnings)

    def test_validation_error_class(self):
        """Test ValidationError exception class."""
        error = ValidationError('title', 'Title is required', 'empty_value')

        assert error.field == 'title'
        assert error.message == 'Title is required'
        assert error.value == 'empty_value'
        assert "field 'title'" in str(error)