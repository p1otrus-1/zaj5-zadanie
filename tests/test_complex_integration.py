
import pytest
from src.manager import Manager
from src.models import Apartment, ApartmentSettlement, Parameters, TenantSettlement, Tenant, Room
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

    assert settlement.total_bills_pln == 150.0 # non-rent bills

    assert settlement.total_rent_pln == 760.0

    assert settlement.total_due_pln == 910.0

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

def test_tenant_settlement():
    parameters = Parameters()
    manager = Manager(parameters)

    #valid tenant
    year = 2025
    month = 1
    apartment_settlement = manager.get_apartment_settlement("apart-polanka", year, month)
    tenant_settlement = manager.get_tenant_settlement(apartment_settlement, "Jan Nowak", year, month)
    assert type(tenant_settlement) == TenantSettlement

    assert tenant_settlement.apartment_settlement == "apart-polanka-2025-1"

    assert tenant_settlement.month == month

    assert tenant_settlement.year == year

    assert tenant_settlement.rent_pln == 760.0 / 3 + 1500.0
    
    assert tenant_settlement.bills_pln == 150.0 /3

    assert tenant_settlement.total_due_pln == 760.0 / 3 + 1500.0 +150.0 /3 

    assert tenant_settlement.balance_pln == 0

    #tenant that lives alone
    manager.apartments["apart-wilda"] = Apartment(
        key = "apart-wilda",
        name = "Wilda",
        location = "Dolna Wilda 1",
        area_m2= 10,
        rooms = {"room": Room(name="room",area_m2=10)}
    )
    manager.tenants["tenant-4"] = Tenant(
        name = "Gal Anonim",
        apartment = "apart-wilda",
        room = "room-1",
        rent_pln = 250.0,
        deposit_pln = 750.0,
        date_agreement_from = "2024-01-01",
        date_agreement_to = "2026-12-31"
    )

    manager.bills.append(Bill(
        apartment='apart-wilda',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=1,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-wilda',
        date_due='2024-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-wilda',
        date_due='2024-02-02',
        settlement_year=2025,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))
    year = 2025
    month = 1
    apartment_settlement = manager.get_apartment_settlement("apart-wilda", year, month)
    tenant_settlement = manager.get_tenant_settlement(apartment_settlement, "Gal Anonim", year, month)
    assert tenant_settlement.tenant == "Gal Anonim"

    assert tenant_settlement.rent_pln == 250.0 + 1250.0

    assert tenant_settlement.bills_pln == 222.0

    assert tenant_settlement.total_due_pln == 250 + 1250.0 + 222.0

    #no tenant
    manager.apartments["apart-puste"] = Apartment(
        key = "apart-puste",
        name = "mieszkanie bez najemcy",
        location = "Dolna Wilda 2",
        area_m2= 10,
        rooms = {"room": Room(name="room",area_m2=10)}
    )
    apartment_settlement = manager.get_apartment_settlement("apart-puste", year, month)
    assert manager.get_tenant_settlement(apartment_settlement, "Gal Anonim", year, month) == None