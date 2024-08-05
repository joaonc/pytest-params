import pytest

from pytest_params import params_values


class TestParamsValues:
    """
    Test ``params_values(...)`` function.
    """

    def test_valid_one_parameter(self):
        name_values = [['name 1', 'value 1']]
        p = params_values(*name_values)

        assert len(p) == 1
        assert p[0].id == 'name 1'
        assert p[0].values == ('value 1',)

    @pytest.mark.parametrize('name_values', [None, [], [['just one entry']]])
    def test_invalid_params_values(self, name_values):
        with pytest.raises(ValueError):
            params_values(name_values)

    def test_mark(self):
        name_values = [
            ['name 1', 'value 1_1', 'value 1_2', pytest.mark.flaky],
            ['name 2', 'value 2_1', 'value 2_2'],
        ]
        p = params_values(*name_values)

        assert len(p) == 2
        assert p[0].id == 'name 1'
        assert p[0].values == ('value 1_1', 'value 1_2')
        assert p[0].marks == [pytest.mark.flaky]
        assert p[1].id == 'name 2'
        assert p[1].values == ('value 2_1', 'value 2_2')
        assert p[1].marks == []

    def test_include_param(self):
        name_values = [[pytest.param('value', id='name')]]
        p = params_values(*name_values)

        assert len(p) == 1
        assert p[0].id == 'name'
        assert p[0].values == ('value',)
        assert p[0].marks == []

    def test_include_param_with_mark_and_mark(self):
        """
        The ``pytest.param(...)`` has a mark and another mark is added.
        """
        name_values = [
            [pytest.param('value', id='name', marks=[pytest.mark.flaky]), pytest.mark.nightly]
        ]
        p = params_values(*name_values)

        assert len(p) == 1
        assert p[0].id == 'name'
        assert p[0].values == ('value',)
        # `MarkDecorator` is not hashable. Using `mark.name` instead.
        assert {mark.name for mark in p[0].marks} == {
            pytest.mark.flaky.name,
            pytest.mark.nightly.name,
        }


class TestParamsValuesUsage:
    """
    Test cases using the ``params_values(...)`` function
    in the ``@pytest.mark.parametrize`` decorator.
    """

    NAME_VALUES_ONE = [['name 1', 'value 1'], ['name 2', 0], ['name 3', None]]
    NAME_VALUES_MULTIPLE = [['name 1', 'value 1', 'value 2'], ['name 2', 0, 1], ['name 3', None, 1]]

    @pytest.mark.parametrize('value', params_values(*NAME_VALUES_ONE))
    def test_valid_one_value(self, request, value):
        name = request.node.name
        expected_name = next(x[0] for x in self.NAME_VALUES_ONE if x[1] == value)

        assert expected_name in name

    @pytest.mark.parametrize('value_1, value_2', params_values(*NAME_VALUES_MULTIPLE))
    def test_valid_multiple_values(self, request, value_1, value_2):
        name = request.node.name
        expected_name = next(
            x[0] for x in self.NAME_VALUES_MULTIPLE if x[1] == value_1 and x[2] == value_2
        )

        assert expected_name in name

    @pytest.mark.parametrize(
        'marks',
        params_values(
            ['one mark', {'flaky'}, pytest.mark.flaky],
            ['two marks', {'flaky', 'performance'}, pytest.mark.flaky, pytest.mark.performance],
            ['out of order', pytest.mark.flaky, {'flaky'}],
        ),
    )
    def test_marks(self, request, marks):
        mark_names = {
            marker.name for marker in request.node.own_markers if marker.name != 'parametrize'
        }
        assert mark_names == marks

    @pytest.mark.parametrize(
        'marks',
        params_values(
            (
                pytest.param(
                    {'flaky', 'nightly'}, id='one param one mark', marks=pytest.mark.flaky
                ),
                pytest.mark.nightly,
            )
        ),
    )
    def test_pytest_param(self, request, marks):
        mark_names = {
            marker.name for marker in request.node.own_markers if marker.name != 'parametrize'
        }
        assert mark_names == marks
