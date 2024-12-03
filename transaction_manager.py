from sites import Site
from transaction import Transaction
import copy

class TransactionManager:
    def __init__(self):
        self.sites = {i: Site(i) for i in range(1, 11)}  # Sites 1 to 10
        self.transactions = {}  
        self.time = 0  

    def begin_transaction(self, transaction_id):
        transaction = Transaction(transaction_id, self.time, self.sites)
        self.transactions[transaction_id] = transaction
        print(f"{transaction_id} begins")

    def read(self, transaction_id, variable_name):
        print(f"{transaction_id} reads {variable_name}")
        self.transactions[transaction_id].read(variable_name)
    
    def write(self, transaction_id, variable_name, value):
        print(f"{transaction_id} writes {variable_name} = {value}")
        self.transactions[transaction_id].write(variable_name, value)

    def end_transaction(self, transaction_id, sites):
        print(f"{transaction_id} ends")
        #if it doesnt return None, then update the sites with the new values it returns
        mysites = self.transactions[transaction_id].commit(sites)
        if mysites:
            self.sites = mysites
            #All the transactions must also update their sites to the new sites
            for transaction in self.transactions.values():
                transaction.sites_snapshot = copy.deepcopy(mysites)
        else:
            #remove transaction from the list of transactions
            del self.transactions[transaction_id]

        print("After end transaction database state:")
        for site in self.sites.values():
            print(site)

    def dump(self):
        # Placeholder for the dump method
        print("Dumping database state:")
        for site in self.sites.values():
            print(site)
         
    def fail_site(self, site_id):
        site = self.sites.get(site_id)
        if site:
            site.fail()
        else:
            print(f"Site {site_id} does not exist")

    def recover_site(self, site_id):
        site = self.sites.get(site_id)
        if site:
            site.recover()
        else:
            print(f"Site {site_id} does not exist")

    def process_command(self, command):
        self.time += 1
        command = command.strip()

        # Handle begin(T1)
        if command.startswith('begin(') and command.endswith(')'):
            transaction_id = command[6:-1]
            self.begin_transaction(transaction_id)
            return

        # Handle R(T1, x2)
        elif command.startswith('R(') and command.endswith(')'):
            inside = command[2:-1]  # Extract the content inside parentheses
            parts = [part.strip() for part in inside.split(',')]
            if len(parts) == 2:
                transaction_id, variable_name = parts
                self.read(transaction_id, variable_name)
            else:
                print(f"Invalid read command: {command}")
            return

        # Handle W(T1, x2, 100)
        elif command.startswith('W(') and command.endswith(')'):
            inside = command[2:-1]
            parts = [part.strip() for part in inside.split(',')]
            if len(parts) == 3:
                transaction_id, variable_name, value = parts
                try:
                    value = int(value)
                    self.write(transaction_id, variable_name, value)
                except ValueError:
                    print(f"Invalid write value: {value}")
            else:
                print(f"Invalid write command: {command}")
            return

        # Handle end(T1)
        elif command.startswith('end(') and command.endswith(')'):
            transaction_id = command[4:-1]
            self.end_transaction(transaction_id, self.sites)
            return

        # Handle dump()
        elif command == 'dump()':
            self.dump()
            return

        # Handle fail(2)
        elif command.startswith('fail(') and command.endswith(')'):
            site_id_str = command[5:-1]
            try:
                site_id = int(site_id_str)
                self.fail_site(site_id)
            except ValueError:
                print(f"Invalid site id: {site_id_str}")
            return

        # handle recover(2)
        elif command.startswith('recover(') and command.endswith(')'):
            site_id_str = command[8:-1]
            try:
                site_id = int(site_id_str)
                self.recover_site(site_id)
            except ValueError:
                print(f"Invalid site id: {site_id_str}")
            return

        else:
            print(f"Unknown command: {command}")
