
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

# How to Run the Program

The program can be executed in two ways: **Using Terminal with Python** or **Using Reprozip**. Follow the steps below based on your preferred method.

---

## 1. Run Using Terminal with Python

1. **Ensure Python 3 is Installed**:
   - Verify Python 3 is installed on your system by running:
     ```bash
     python --version
     ```
     or
     ```bash
     python3 --version
     ```

2. **Prepare Input Files**:
   - Add all input files you want to test to the `./inputs` folder.
   - Ensure that input files are in `.txt` format.

3. **Run the Program**:
   - Navigate to the project directory where the `main.py` file is located.
   - Execute the following command:
     ```bash
     python main.py
     ```
     or, if `python` points to Python 2:
     ```bash
     python3 main.py
     ```

4. **View Output**:
   - The program will process all `.txt` files in the `./inputs` folder.
   - Output will be printed to the terminal (stdout) sequentially for all files. Note: The output is **not sorted** based on file processing order.

---

## 2. Run Using Reprozip

Reprozip enables creating and running reproducible execution environments. Follow these steps to create and run a Reprozip-based environment:

### A. Create a Reprozip File

1. **Trace Execution**:
   - Run the following command in the project directory to trace the program's execution:
     ```bash
     reprozip trace python main.py
     ```

2. **Pack the Execution**:
   - Create a `.rpz` file using the following command:
     ```bash
     reprozip pack SSI
     ```
   - This generates an archive (`SSI.rpz`) containing all required dependencies and configurations.

---

### B. Run the Program Using Reprounzip

1. **Unpack the `.rpz` File**:
   - Set up the directory to run the program:
     ```bash
     reprounzip directory setup SSI.rpz SSI
     ```
   - This command creates an `SSI` folder with all required files.

2. **Run the Program**:
   - Execute the program within the Reprounzip environment:
     ```bash
     reprounzip directory run SSI
     ```

3. **Modify Input Files**:
   - To add or change input files:
     - Navigate to the appropriate directory:
       ```bash
       cd /SSI/root/home/pvg2018/Serializable_SnapShot_Isolation/
       ```
     - Place your `.txt` input files in the `inputs` folder.

4. **Re-run the Program**:
   - After modifying inputs, re-run the program using:
     ```bash
     reprounzip directory run SSI
     ```

---

This setup ensures reproducibility and allows you to test the program with different input configurations efficiently.


# Project Overview

This project implements Serializable Snapshot Isolation (SSI) in a replicated, distributed database system. It provides robust concurrency control and handles site failures and recoveries while maintaining transactional consistency and serializability.

## Serializable Snapshot Isolation (SSI)

- **Snapshots**: Each transaction operates on its own consistent snapshot of the database, taken at the start of the transaction.
- **Reads**: Transactions read from their snapshot, ensuring a stable view of data throughout execution.
- **Writes**: Changes made by a transaction are buffered locally and only apply to the database at commit time.
- **Validation**: At commit, the transaction’s initial snapshot is compared against the global state to ensure no conflicts have occurred since its start. It also constructs a Transaction serialization graph. At each commit time, we check if there exists a cycle where there are two consecutive RW edges. If they exist, we should abort the transaction that is causing the cycle with two RW edges.

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
  - **Abort**: On detection of conflicts or site failure issues, or cycle with two consecuitive RW edges in the serialization graph the transaction’s changes are discarded.

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

