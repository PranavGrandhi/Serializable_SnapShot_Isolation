from sites import Site
from transaction import Transaction
import copy

class TransactionManager:
    def __init__(self):
        self.sites = {i: Site(i) for i in range(1, 11)}  # Sites 1 to 10
        # for site in self.sites.values():
        #     site.commitTime = 0
        # for site in self.sites.values():
        #    site.failTime = []
        self.transactions = {}  
        self.time = 0
        self.last_commits = {}  
        self.serialization_graph = {} # Adj list
        self.overall_reads = {} # Dict of variable name to list of transactions that read it
        self.overall_writes = {} # Dict of variable name to list of transactions that write it
        self.waiting_transactions = {} # Dict of variable name to list of transactions that are waiting for it
        self.verbose = False

    def begin_transaction(self, transaction_id):
        transaction = Transaction(transaction_id, self.time, self.sites, self)
        self.transactions[transaction_id] = transaction
        print(f"{transaction_id} begins")

    def detect_cycle(self):
        visited = {}

        def dfs(txn, path, edge_types):
            visited[txn] = 'gray'
            path.append(txn)

            for neighbor, edge_type in self.serialization_graph.get(txn, []):
                if neighbor not in visited:
                    # Continue DFS traversal
                    if dfs(neighbor, path, edge_types + [edge_type]):
                        return True
                elif visited[neighbor] == 'gray':
                    # Cycle detected: extract the cycle path
                    cycle_start_index = path.index(neighbor)
                    cycle_edge_types = edge_types[cycle_start_index:]
                    cycle_edge_types.append(edge_type)  # Include the closing edge

                    # Debugging: Print the cycle and its edge types
                    cycle_path = path[cycle_start_index:] + [neighbor]
                    print(f"Cycle detected: {' -> '.join(cycle_path)} with edge types {cycle_edge_types}")

                    # Check for two consecutive 'RW' edges, including wrap-around
                    for i in range(len(cycle_edge_types)):
                        current_edge = cycle_edge_types[i]
                        next_edge = cycle_edge_types[(i + 1) % len(cycle_edge_types)]
                        if current_edge == 'RW' and next_edge == 'RW':
                            print(f"Consecutive 'RW' edges found: {current_edge} -> {next_edge}")
                            return True  # Problematic cycle detected

            path.pop()
            visited[txn] = 'black'
            return False

        for txn in self.serialization_graph:
            if txn not in visited:
                if dfs(txn, [], []):
                    return True  # Problematic cycle found

        return False  # No problematic cycles detected
    
    def remove_transaction(self, txn_id):
        """
        Removes a transaction and all its edges (both incoming and outgoing) from the serialization graph.

        Args:
            txn_id (str): The ID of the transaction to be removed.
        """
        # Remove all outgoing edges from txn_id
        if txn_id in self.serialization_graph:
            del self.serialization_graph[txn_id]
            print(f"Removed transaction {txn_id} and its outgoing edges from the serialization graph.")

        # Remove all incoming edges to txn_id
        transactions_to_update = []
        for txn, edges in self.serialization_graph.items():
            # Filter out edges that point to txn_id
            original_edge_count = len(edges)
            self.serialization_graph[txn] = [edge for edge in edges if edge[0] != txn_id]
            if len(self.serialization_graph[txn]) < original_edge_count:
                transactions_to_update.append(txn)

        if self.verbose:
            if transactions_to_update:
                print(f"Removed incoming edges to {txn_id} from transactions: {', '.join(transactions_to_update)}.")
            else:
                print(f"No incoming edges to {txn_id} were found in the serialization graph.")

    def read(self, transaction_id, variable_name):
        #Add variable -> transaction mapping to overall reads if the transaction_id is not available already
        #last commit time<site failure time<transaction start time

        if variable_name not in self.overall_reads:
            self.overall_reads[variable_name] = [(transaction_id, self.time)]
        else:
        # Check if transaction_id is already associated with the variable
            existing_transactions = [entry[0] for entry in self.overall_reads[variable_name]]
            if transaction_id not in existing_transactions:
                self.overall_reads[variable_name].append((transaction_id, self.time))


        if transaction_id not in self.transactions:
            print(f"{transaction_id} Aborted so not available to read")
        else:
            #print(f"{transaction_id} reads {variable_name}")
            self.transactions[transaction_id].read(variable_name)
    
    def write(self, transaction_id, variable_name, value):
        #Add variable -> transaction mapping to overall writes if the transaction_id is not available already
        if variable_name not in self.overall_writes:
            self.overall_writes[variable_name] = [(transaction_id, self.time)]
        else:
            existing_transactions = [entry[0] for entry in self.overall_writes[variable_name]]
            if transaction_id not in existing_transactions:
                self.overall_writes[variable_name].append((transaction_id, self.time))

        if transaction_id not in self.transactions:
            print(f"{transaction_id} Aborted so not available to write")
            return
        else:
            if self.verbose:
                print(f"{transaction_id} writes {variable_name} = {value}")
            self.transactions[transaction_id].write(variable_name, value)

    def end_transaction(self, transaction_id, sites):
        if transaction_id not in self.transactions:
            print(f"{transaction_id} Aborted so not available to end")
            return
        print(f"{transaction_id} ends")
        #if it doesnt return None, then update the sites with the new values it returns
        mysites_snapshot = self.transactions[transaction_id].commit(sites)
        if mysites_snapshot:
            # Merge the changes from the transaction's snapshot into the global sites
            for site_id, site in mysites_snapshot.items():
                global_site = self.sites[site_id]
                #global_site.last_commit = self.time
                if global_site.is_up:
                    # Update the variables in the global site with the values from the transaction's snapshot
                    for variable_name, variable in site.variables.items():
                        if variable_name in self.transactions[transaction_id].variables_write:
                            # global_site.commitTime = self.time
                            global_site.variables[variable_name].value = variable.value

                            #If the commited value is not equal to the already present value in global site then update the commit time with var, commit time
                            if global_site.variables[variable_name].value != variable.value:
                                global_site.commitTime[variable_name] = self.time
                            
                            print(f"{transaction_id} commits {variable_name} = {variable.value} to Site {site_id}")
            del self.transactions[transaction_id]
        else:
            #remove transaction from the list of transactions
            del self.transactions[transaction_id]
        if self.verbose:
            print("After end transaction database state:")
            for site in self.sites.values():
                print(site)

    def abort_transaction(self, transaction_id):
        if transaction_id not in self.transactions:
            print(f"{transaction_id} Aborted so not available to abort")
            return
        print(f"{transaction_id} aborts")
        self.transactions[transaction_id].abort()
        del self.transactions[transaction_id]

    def dump(self):
        # Placeholder for the dump method
        print("Dumping database state:")
        for site in self.sites.values():
            print(site)
         
    def fail_site(self, site_id):
        site = self.sites.get(site_id)

        # Go through all the transactions and if they have a write on the site that failed, 
        # then abort and remove the transaction.
        transactions_to_remove = []
        for transaction in self.transactions.values():
            for variable_name in transaction.variables_write:
                print(f"Site {site_id} failed")
                if variable_name in site.variables:
                    #print(f"{transaction.transaction_id} aborts because site {site_id} failed")
                    transaction.abort()
                    transactions_to_remove.append(transaction.transaction_id)
            transaction.sites_snapshot[site_id].is_up = False
        for transaction_id in transactions_to_remove:
            del self.transactions[transaction_id]

        # Saving the fail time of the site in the FailTime list of the site
        site.failTime.append(self.time)

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

        global_site = copy.deepcopy(self.sites[site_id])
        for transaction in self.transactions.values():
            transaction.sites_snapshot[site_id] = copy.deepcopy(global_site)
            transaction.sites_snapshot[site_id].is_up = True
        # Go through waiting transactions and check if they can be read now
        #   waiting_transactions: {2: [('T3', 'x8', 2)]}
        print(f"Site {site_id} recovered")
        print(f"Waiting transactions: {self.waiting_transactions}")
        if site_id in self.waiting_transactions:
            for transaction_id, variable_name,recovered_site_id in self.waiting_transactions[site_id]:
                if recovered_site_id == site_id:
                    self.read(transaction_id, variable_name) 

    def process_command(self, command):
        if '//' in command:
            command = command.split('//', 1)[0].strip()

        # If after removing comments the line is empty, just return
        if not command:
            return
        
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
