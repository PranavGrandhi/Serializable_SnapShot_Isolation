import copy
class Transaction:
    def __init__(self, transaction_id, start_time, sites, manager):
        self.transaction_id = transaction_id
        self.start_time = start_time
        self.initial_sites = copy.deepcopy(sites)
        self.variables_write = set()  # set of variables written by this transaction
        self.sites_snapshot = copy.deepcopy(sites) # snapshot of the sites at the start of the transaction
        self.is_active = True
        self.manager = manager

    def read(self, variable_name):
        for i in range(1, 11):
            site = self.sites_snapshot[i]
            #if the site is up and the variable is present in the site then read the value of it
            if site.is_up and variable_name in site.variables:
                print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")

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
         # Instead of comparing initial_value and current_value, do "first committer wins" check.
        for variable_name in self.variables_write:
            last_commit_time = self.manager.last_commits.get(variable_name, -1)
            
            # If some other transaction committed this variable after we started, abort.
            if last_commit_time > self.start_time:
                print(f"{self.transaction_id} aborts because {variable_name} was already committed by another transaction after we started")
                self.abort()
                return None

        # If we reach here, we can commit
        print(f"{self.transaction_id} commits")

        # Update last commit times for the variables we wrote
        for variable_name in self.variables_write:
            self.manager.last_commits[variable_name] = self.manager.time

        return self.sites_snapshot
    
    def abort(self):
        self.is_active = False
        print(f"{self.transaction_id} aborts")

    def __repr__(self):
        return f"Transaction {self.transaction_id}"
