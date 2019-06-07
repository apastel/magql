from inflection import pluralize

from tests.conftest import House, Car, Person, base
from magql.resolver_factory import SingleResolver, CreateResolver, DeleteResolver, ManyResolver, UpdateResolver

import pytest


class DummyInfo:
    def __init__(self, session):
        self.context = session


@pytest.fixture
def info(session):
    return DummyInfo(session)


def compare(output, test_input):
    for key, value in test_input.items():
        output_value = getattr(output, key)
        if isinstance(output_value, list):
            for instance in output_value:
                if isinstance(instance, base):
                    assert instance.id in value
        elif isinstance(output_value, base):
            assert output_value.id == value
        else:
            assert output_value == value


@pytest.mark.parametrize("input_data", [
    (House, {"name": "House 2", "inhabitants": [1]}),
    (Car, {"name": "Car 2", "drivers": [1]}),
    (Person, {"name": "Person 2", "age": 30, "car": 1, "house": 1})
])
def test_create_resolver(input_data, info, session):
    test_class = input_data[0]
    test_input = input_data[1]
    table_name = test_class.__tablename__
    resolve = CreateResolver(test_class.__table__)

    output = resolve(None, info, input=test_input)[table_name]

    compare(output, test_input)


@pytest.mark.parametrize("input_data", [
    (House, 1, {"name": "House 2", "inhabitants": [1]}),
    (Car, 1, {"name": "Car 2", "drivers": [1]}),
    (Person, 1, {"name": "Person 2", "age": 30, "car": 1, "house": 1})
])
def test_update_resolver(input_data, info, session):
    test_class = input_data[0]
    test_id = input_data[1]
    test_input = input_data[2]
    table_name = test_class.__tablename__
    resolve = UpdateResolver(test_class.__table__)

    output = resolve(None, info, id=test_id, input=test_input)[table_name]

    compare(output, test_input)


@pytest.mark.parametrize("input_data", [
    (House, 1),
    (Car, 1),
    (Person, 1)
])
def test_delete_resolvers(input_data, info, session):
    test_class = input_data[0]
    test_id = input_data[1]
    table_name = test_class.__tablename__
    resolve = DeleteResolver(test_class.__table__)

    resolve(None, info, id=test_id)[table_name]

    assert session.query(test_class).filter_by(id=test_id).one_or_none() is None


@pytest.mark.parametrize("model", [House, Car, Person])
@pytest.mark.parametrize("model_id", [1, 2])
def test_single_resolvers(model, model_id, session, info):
    resolver = SingleResolver(model.__table__)
    resolved_value = resolver(None, info, id=model_id)
    queried_value = session.query(model).filter_by(id=model_id).one_or_none()
    assert queried_value == resolved_value
