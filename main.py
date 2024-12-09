from transaction_manager import TransactionManager
import os

def process_input(input_file, input_folder):
    tm = TransactionManager()
    input_file = os.path.join(input_folder, input_file)

    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('//'):
                tm.time += 1
                continue
            print(f"> {line}")
            tm.process_command(line)

def main():
    input_folder = './inputs'
    #iterate through all the input files in the input folder and call process input on the files
    for file in os.listdir(input_folder):
        print(f"Processing {file}")
        process_input(file, input_folder)
        print("--------------------------------------------------------------------------------------")

if __name__ == '__main__':
    main()
