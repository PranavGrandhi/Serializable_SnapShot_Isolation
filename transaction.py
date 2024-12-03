import copy
class Transaction:
    def __init__(self, transaction_id, start_time, sites):
        self.transaction_id = transaction_id
        self.start_time = start_time
        self.initial_sites = copy.deepcopy(sites)
        self.variables_write = set()  # set of variables written by this transaction
        self.sites_snapshot = copy.deepcopy(sites) # snapshot of the sites at the start of the transaction
        self.is_active = True

    def read(self, variable_name, sites):
        # Implement reading logic according to SSI rules
        pass

    def write(self, variable_name, value):
        for i in range(1, 11):
            site = self.sites_snapshot[i]
            #if the site is up and the variable is present in the site then change the value of it
            if site.is_up and variable_name in site.variables:
                site.variables[variable_name].value = value
                self.variables_write.add(variable_name)
                print(f"{self.transaction_id} writes {variable_name} = {value} at site {site.site_id}")

        #print the state of the sites after writing
        print("After writing:")
        for site in self.sites_snapshot.values():
            print(site)

    # returns the new value of the sites if the transaction is not aborted. Or else it sends the abort signal and returns null
    def commit(self, current_sites):
        # Check if the variables written by this transaction have been changed by others
        should_abort = False
        for variable_name in self.variables_write:
            print(f"Checking {variable_name}")
            initial_value = None
            current_value = None
            # Find the initial value from initial_sites
            for i in range(1, 11):
                site = self.initial_sites[i]
                if variable_name in site.variables:
                    initial_value = site.variables[variable_name].value
                    break
            # Find the current value from current_sites
            for i in range(1, 11):
                site = current_sites[i]
                if variable_name in site.variables:
                    current_value = site.variables[variable_name].value
                    break
            if initial_value is None or current_value is None:
                # Variable not found; abort
                print(f"{self.transaction_id} aborts because {variable_name} not found in sites")
                should_abort = True
                break
            if initial_value != current_value:
                # The variable has been modified since the transaction began
                print(f"{self.transaction_id} aborts because {variable_name} was modified by another transaction")
                should_abort = True
                break
        if should_abort:
            self.abort()
            return None
        else:
            print(f"{self.transaction_id} commits")
            return self.sites_snapshot
    
    def abort(self):
        self.is_active = False
        print(f"{self.transaction_id} aborts")

    def __repr__(self):
        return f"Transaction {self.transaction_id}"
