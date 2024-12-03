
# Transaction Management System (Serializable Snapshot Isolation Simulation  in Databases)

This project implements a simple distributed transaction management system that simulates the behavior of transactions, sites, and variables in a database following the Serializable Snapshot Isolation (SSI) protocol. It manages read and write operations with proper isolation and concurrency control, ensuring serializability in a distributed environment.

## Project Structure

- **`variable.py`**: Defines the `Variable` class representing a variable with a name and value.
- **`site.py`**: Defines the `Site` class representing a site that holds variables. Each site can be up or down and maintains its own set of variables.
- **`transaction.py`**: Defines the `Transaction` class representing a transaction with its own local snapshot and write set.
- **`transaction_manager.py`**: Defines the `TransactionManager` class that manages transactions, sites, and processes input commands.
- **`main.py`**: The main entry point of the program that reads input commands from `input.txt` and executes them.
- **`input.txt`**: A text file containing the commands to be executed by the transaction manager.

## How to Provide Input

The input commands should be written in the `input.txt` file. Each command should be on a separate line. Empty lines or lines starting with `//` are considered comments or time advancement.

### Command Format

- **Begin Transaction**: `begin(Tx)` where `Tx` is the transaction ID.
- **Read Operation**: `R(Tx, xN)` where `Tx` is the transaction ID and `xN` is the variable name.
- **Write Operation**: `W(Tx, xN, value)` where `Tx` is the transaction ID, `xN` is the variable name, and `value` is the integer value to write.
- **End Transaction**: `end(Tx)` where `Tx` is the transaction ID.
- **Dump State**: `dump()`
- **Fail Site**: `fail(N)` where `N` is the site ID (1 to 10).
- **Recover Site**: `recover(N)` where `N` is the site ID (1 to 10).

### Example Input (`input.txt`)

```
// Test 1: T1 should abort, T2 should not, because T2 committed first and they both wrote x1 and x2.

begin(T1)
begin(T2)
W(T1,x1,101) 
W(T2,x2,202)
W(T1,x2,102) 
W(T2,x1,201)
end(T2)
end(T1)
dump()
```

## How to Run the Program

1. **Ensure Python 3 is Installed**: Verify that Python 3 is installed on your system by running `python --version` or `python3 --version`.

2. **Prepare the Input File**: Edit the `input.txt` file to include the commands you wish to execute.

3. **Run the Program**:

   Open a terminal or command prompt in the project directory and execute:

   ```bash
   python main.py
   ```

   or, if `python` points to Python 2 on your system:

   ```bash
   python3 main.py
   ```

4. **View the Output**: The program will read commands from `input.txt`, execute them, and print the output to the console.

## Project Details

### Serializable Snapshot Isolation (SSI)

The system uses SSI to manage transaction isolation and ensure serializability:

- **Snapshots**: Each transaction operates on its own snapshot of the database, taken at the start of the transaction.
- **Reads**: Transactions read data from their snapshot, ensuring a consistent view of the database state.
- **Writes**: Writes are stored in the transaction's local workspace and applied to the database upon a successful commit.
- **Validation**: At commit time, transactions check for conflicts by comparing their initial snapshot with the current database state.

### Sites and Variables

- **Sites**: There are 10 sites, each with a unique site ID from 1 to 10. Sites can be up or down.
- **Variables**:
  - Variables `x1` to `x20` are distributed across the sites.
  - **Even-Indexed Variables** (`x2`, `x4`, ..., `x20`):
    - Replicated at all sites.
    - Available as long as at least one site is up.
  - **Odd-Indexed Variables** (`x1`, `x3`, ..., `x19`):
    - Stored at a single site, calculated as `1 + (index mod 10)`.
    - For example, `x1` and `x11` are at site 2, `x3` and `x13` are at site 4.
- **Variable Initialization**: All variables are initialized to `10 * index`. For example, `x1 = 10`, `x2 = 20`, ..., `x20 = 200`.

### Transactions

- **Begin**: Transactions begin with a snapshot of the current database state.
- **Read/Write Operations**:
  - **Reads**: Return the value of a variable from the transaction's snapshot.
  - **Writes**: Stored in the transaction's local write set and applied upon commit.
- **End**: When a transaction ends, it attempts to commit:
  - **Commit**: If validation passes (no conflicts), writes are applied to the database.
  - **Abort**: If validation fails (conflicts detected), the transaction aborts, and changes are discarded.

### Concurrency Control

- **Conflict Detection**: At commit time, transactions check if any variables they intend to write have been modified by other transactions since they began.
- **First-Committer-Wins Rule**: If a conflict is detected, the transaction attempting to commit later aborts.
- **Isolation**: Transactions operate independently without interfering with each other's snapshots.

### Site Failures and Recovery

- **Failing a Site**: Use `fail(N)` to bring down site `N`.
- **Recovering a Site**: Use `recover(N)` to bring site `N` back up.
- **Impact on Transactions**: Transactions must handle site availability when performing operations. If a site fails, variables stored exclusively at that site become unavailable.

---
