
# Transaction Management System (Serializable Snapshot Isolation Simulation  in Databases)

This project implements a simple distributed transaction management system that simulates the behavior of transactions, sites, and variables in a database following the Serializable Snapshot Isolation (SSI) protocol. It manages read and write operations with proper isolation and concurrency control, ensuring serializability in a distributed environment.

## Project Structure

- **`variable.py`**: Defines the `Variable` class representing a variable with a name and value.
- **`site.py`**: Defines the `Site` class representing a site that holds variables. Each site can be up or down and maintains its own set of variables.
- **`transaction.py`**: Defines the `Transaction` class representing a transaction with its own local snapshot and write set.
- **`transaction_manager.py`**: Defines the `TransactionManager` class that manages transactions, sites, and processes input commands.
- **`main.py`**: The main entry point of the program that reads input commands from `input.txt` and executes them.
- **`./inputs`**: A Folder containing all the input files that will get run everytime Python main.py is run.

## How to Provide Input

The input commands should be written in the a .txt file and added to the folder called './inputs/' Each command should be on a separate line. Empty lines or lines starting with `//` are considered comments or time advancement.

### Command Format

- **Begin Transaction**: `begin(Tx)` where `Tx` is the transaction ID.
- **Read Operation**: `R(Tx, xN)` where `Tx` is the transaction ID and `xN` is the variable name.
- **Write Operation**: `W(Tx, xN, value)` where `Tx` is the transaction ID, `xN` is the variable name, and `value` is the integer value to write.
- **End Transaction**: `end(Tx)` where `Tx` is the transaction ID.
- **Dump State**: `dump()`
- **Fail Site**: `fail(N)` where `N` is the site ID (1 to 10).
- **Recover Site**: `recover(N)` where `N` is the site ID (1 to 10).

### Example Input (`./inputs/input1.txt`)

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

# Project Overview

This project implements Serializable Snapshot Isolation (SSI) in a replicated, distributed database system. It provides robust concurrency control and handles site failures and recoveries while maintaining transactional consistency and serializability.

## Serializable Snapshot Isolation (SSI)

- **Snapshots**: Each transaction operates on its own consistent snapshot of the database, taken at the start of the transaction.
- **Reads**: Transactions read from their snapshot, ensuring a stable view of data throughout execution.
- **Writes**: Changes made by a transaction are buffered locally and only apply to the database at commit time.
- **Validation**: At commit, the transaction’s initial snapshot is compared against the global state to ensure no conflicts have occurred since its start.

## Sites and Variables

- **Sites (1–10)**: The database is spread across 10 sites. Each site can independently fail or recover.
- **Variables**:
  - **Even-Indexed** (`x2`, `x4`, ..., `x20`): Replicated across all sites, ensuring higher availability.
  - **Odd-Indexed** (`x1`, `x3`, ..., `x19`): Stored at exactly one site, determined by `1 + (index mod 10)`.
- **Initialization**: All variables `x1` to `x20` start with values set to `10 * index`.

## Transactions

- **Begin**: A new transaction takes a snapshot of the current database state.
- **Operations**:
  - **Read**: Returns the value from the snapshot, unaffected by concurrent writes.
  - **Write**: Temporarily held in the transaction’s workspace. They become durable only after commit.
- **End (Commit/Abort)**:
  - **Commit**: If no conflicts are found, changes are written to the database.
  - **Abort**: On detection of conflicts or site failure issues, the transaction’s changes are discarded.

## Concurrency Control

- **Conflict Detection**: Ensures that if a variable was modified by another transaction post-snapshot, the current transaction’s commit will fail.
- **First-Committer-Wins**: If two transactions modify the same data, the one that attempts to commit later will abort.
- **Isolation**: Ensures that transactions behave as if they were executed sequentially.

## Site Failures and Recovery

- **fail(N)**: Marks site `N` as down, making data at that site unavailable.
- **recover(N)**: Brings site `N` back up. Replicated variables become write-available immediately, but read-availability requires a post-recovery commit.
- **Transaction Impact**: Transactions adapt to site availability. If a required site is down and data is not replicated elsewhere, the transaction may have to wait or abort.

---

By adhering to SSI, this system balances consistency, availability, and fault tolerance, creating a foundation for reliable distributed database operations.

