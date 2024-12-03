from variable import Variable

class Site:
    def __init__(self, site_id):
        self.site_id = site_id # from 1 to 10
        self.variables = {}  # Key: variable name, Value: num
        self.is_up = True 
        self.initialize_variables()

    def initialize_variables(self):
         for i in range(1, 21):
            if i % 2 == 0 or (1 + (i % 10)) == self.site_id:
                var_name = f"x{i}"
                self.variables[var_name] = Variable(var_name, 10 * i)

    def fail(self):
        self.is_up = False

    def recover(self):
        self.is_up = True

    def __repr__(self):
        vars_list = sorted(self.variables.values(), key=lambda v: int(v.name[1:]))
        vars_str = ', '.join(str(var) for var in vars_list)
        return f"Site {self.site_id} -- {vars_str}"
