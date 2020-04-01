# -*- coding: utf-8 -*-
"""Tests for the `provider` module."""

from unittest.mock import Mock

from certificate_validator.data_mapper import (
    ClassValue, CleanListValue, DataMapper, DataMapperValue
)

from .base import BaseTestCase


class CustomDataMapper(DataMapper):

    MAP = {
        'ValueDefault': DataMapperValue('value_default', default="default"),
        'ValueEmpty': DataMapperValue('value_empty', default=""),
        'ValueNoDefault': DataMapperValue('value_no_default', default=""),
        'ValueNone': DataMapperValue('value_none', default=None)
    }


class DataMapperValueTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_data_mapper_value_default_and_parser(self):
        parser = Mock()
        parser.return_value = 'return_value'
        value = DataMapperValue(
            'value_default', default="default", parser=parser
        )
        self.assertEquals('value_default', value.param)
        self.assertEquals('default', value.default)
        parser.assert_not_called()
        self.assertEquals('return_value', value.parsed('custom'))
        parser.assert_called_once_with('custom')

    def test_data_mapper_value_default_and_no_parser(self):
        value = DataMapperValue('value_default', default="default")
        self.assertEquals('value_default', value.param)
        self.assertEquals('default', value.default)
        self.assertEquals('custom', value.parsed('custom'))

    def test_data_mapper_value_no_default_and_no_parser(self):
        value = DataMapperValue('value_default')
        self.assertEquals('value_default', value.param)
        self.assertEquals('', value.default)
        self.assertEquals('custom', value.parsed('custom'))

    def test_data_mapper_value_none_default_and_no_parser(self):
        value = DataMapperValue('value_default', default=None)
        self.assertEquals('value_default', value.param)
        self.assertIsNone(value.default)
        self.assertEquals('custom', value.parsed('custom'))


class CleanListValueTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_empty_default(self):
        test_cases = [
            (None, []),
            ([], []),
            ([None], []),
            ([''], []),
            (['-'], []),
            ([None, ''], []),
            ([None, '-'], []),
            ([None, '', '-'], []),
        ]

        value = CleanListValue('value')

        for test_case, expected in test_cases:
            actual = value.parsed(test_case)
            self.assertEqual(
                expected, actual,
                "Failed clean_list({}) - expected {}, got {}".format(
                    test_case, expected, actual
                )
            )

    def test_non_empty_default(self):
        test_cases = [
            ([None, 'value'], ['value']),
            (['value'], ['value']),
            (['value', None], ['value']),
            (['', 'value'], ['value']),
            (['value', ''], ['value']),
            (['-', 'value'], ['value']),
            (['value', '-'], ['value']),
            ([None, 'value', ''], ['value']),
            ([None, 'value', '-'], ['value']),
            ([None, 'value', '', '-'], ['value']),
        ]

        value = CleanListValue('value')

        for test_case, expected in test_cases:
            actual = value.parsed(test_case)
            self.assertEqual(
                expected, actual,
                "Failed clean_list({}) - expected {}, got {}".format(
                    test_case, expected, actual
                )
            )


class ClassValueTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_empty(self):
        value = ClassValue('value', clazz=CustomDataMapper)
        parsed = value.parsed({})
        self.assertIsInstance(parsed, CustomDataMapper)
        self.assertEqual(parsed.value_default, 'default')
        self.assertEqual(parsed.value_empty, '')
        self.assertEqual(parsed.value_no_default, '')
        self.assertIsNone(parsed.value_none)

    def test_values(self):
        value = ClassValue('value', clazz=CustomDataMapper)
        parsed = value.parsed({
            'extra': value,
            'ValueDefault': 'ValueDefault',
            'ValueEmpty': 'ValueEmpty',
        })
        self.assertIsInstance(parsed, CustomDataMapper)
        self.assertEqual(parsed.value_default, 'ValueDefault')
        self.assertEqual(parsed.value_empty, 'ValueEmpty')
        self.assertEqual(parsed.value_no_default, '')
        self.assertIsNone(parsed.value_none)
