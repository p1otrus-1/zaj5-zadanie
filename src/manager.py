from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        if apartment_key not in self.apartments:
            return None
        if month is not None:
            if month >= 13:
                raise Exception("Nieprawidłowy miesiąc")

        sum = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if bill.settlement_year == year or year == None:
                    if bill.settlement_month == month or month == None:
                        sum+=bill.amount_pln
        return sum

    def get_apartment_settlement(self, apartment_key: str, year: int , month: int)-> ApartmentSettlement:
        if apartment_key not in self.apartments:
            raise Exception("apartment nie istnieje")
        if month >= 13:
            raise Exception("Nieprawidłowy miesiąc")
        total_rent = 0.0
        #for tenant in self.tenants.values():
        #    if tenant.apartment == apartment_key:
        #        total_rent += tenant.rent_pln
        #        print(tenant.name, ":", tenant.rent_pln)
        
        total_bills = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if bill.settlement_month == month and bill.settlement_year == year:
                    if bill.type == "rent":
                        total_rent += bill.amount_pln
                    else:
                        total_bills += bill.amount_pln
        total_due = total_rent + total_bills
        
        
        return ApartmentSettlement(apartment=apartment_key, month=month, year=year, total_rent_pln=total_rent, total_bills_pln=total_bills, total_due_pln=total_due)

    def get_tenant_settlement(self, apartment_settlement: ApartmentSettlement, tenant_name: str, year: int, month: int)-> TenantSettlement | None:
        tenant = tenant_name
        apartment_str = f"{apartment_settlement.apartment}-{year}-{month}"
        rent = 0
        nr_tenants = 0
        
        for tenant in self.tenants.values():
            if tenant.apartment == apartment_settlement.apartment:
                nr_tenants += 1
            if tenant.name == tenant_name:
                rent += tenant.rent_pln
        if nr_tenants == 0:
            return None
        bills = 0
        for bill in self.bills:
            if bill.apartment == apartment_settlement.apartment:
                if bill.settlement_month == month and bill.settlement_year == year:
                    if bill.type == "rent":
                        rent += bill.amount_pln / nr_tenants
                    else:
                        bills += bill.amount_pln / nr_tenants
        total_due = rent + bills
        balance = 0

        return TenantSettlement(
            tenant=tenant_name,
            apartment_settlement= apartment_str,
            month=month,
            year=year,
            rent_pln=rent,
            bills_pln=bills,
            total_due_pln=total_due,
            balance_pln=balance
        )