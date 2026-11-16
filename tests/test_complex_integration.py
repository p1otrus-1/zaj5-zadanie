from src.models import Apartment
from src.manager import Manager
from src.models import Parameters 


def test_apartment_not_exist():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs("non-existant", 2026, 11) == None

def test_no_bills():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs("apart-polanka", 2026, 11) == 0.0

def test_bills_sum():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910.0
    