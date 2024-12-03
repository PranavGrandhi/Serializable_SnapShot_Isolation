from transaction_manager import TransactionManager

def main():
    tm = TransactionManager()
    input_file = 'input.txt'

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('//'):
                tm.time += 1
                continue
            print(f"> {line}")
            tm.process_command(line)

if __name__ == '__main__':
    main()
