

class Router:
    def __init__(self, methods):
        self.methods = methods

    def excel_uploader(self, identifier):
        if identifier == "users":
            return self.methods.users_list()
        elif identifier == "employees":
            return self.methods.employees_list()
        elif identifier == "departments":
            return self.methods.departments()
        elif identifier == "teams":
            return self.methods.teams()
        elif identifier == "positions":
            return self.methods.positions()
        elif identifier == "deduction_categories":
            return self.methods.deduction_categories()
        elif identifier == "allowance_categories":
            return self.methods.allowance_categories()
        elif identifier == "leave_types":
            return self.methods.leave_types()
        elif identifier == "contracts":
            return self.methods.contract()
        elif identifier == "schedules":
            return self.methods.schedules()
        elif identifier == "schedule_lines":
            return self.methods.schedule_lines()
        elif identifier == "deductions":
            return self.methods.deductions()
        elif identifier == "leaves":
            return self.methods.leaves()
        elif identifier == "addresses":
            return self.methods.addresses()
        elif identifier == "allowances":
            return self.methods.allowances()
        elif identifier == "previous_employers":
            return self.methods.previous_employers()
        elif identifier == "banks":
            return self.methods.banks()
