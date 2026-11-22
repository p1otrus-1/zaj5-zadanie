
import pytest
from src.manager import Manager
from src.models import ApartmentSettlement, Parameters
from src.models import Bill


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

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
    
def test_wrong_month():
    parameters = Parameters()
    manager = Manager(parameters)
    with pytest.raises(Exception) as e_info:
        _ = manager.get_apartment_costs("apart-polanka", 2025, 13)

#==============TDD - krok 4==============

def test_apartment_settlement():
    parameters = Parameters()
    manager = Manager(parameters)
    
    #month with bills
    apartment = "apart-polanka"
    year = 2025
    month = 1
    settlement = manager.get_apartment_settlement(apartment, year, month)
    
    assert type(settlement) == ApartmentSettlement

    assert settlement.total_bills_pln == 910.0

    assert settlement.total_rent_pln == 760.0

    assert settlement.total_due_pln == 1670.0

    #apartment, year, month in object
    assert settlement.apartment == apartment

    assert settlement.year == year

    assert settlement.month == month
    
    #month without bills
    settlement = manager.get_apartment_settlement("apart-polanka",2025,10)
    assert settlement.total_bills_pln == 0

    assert settlement.total_rent_pln == 0

    assert settlement.total_due_pln == 0

    #invalid apartment name
    with pytest.raises(Exception) as e_info:
        _ = manager.get_apartment_settlement("non-existant", 2025, 1)

    #invalid month
    with pytest.raises(Exception) as e_info:
        _ = manager.get_apartment_settlement("apart-polanka", 2025, 13)

    

    