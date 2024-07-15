import os


class BasicASMInterpreter:
    def __init__(self):
        self.memory = [0] * 1000
        self.registers = {"R1": 0, "R2": 0, "R3": 0, "R4": 0}
        self.stack = []
        self.program_counter = 0
        self.labels = {}
        self.instructions = []
        self.comparison_flag = None

    def parse(self, code):
        lines = code.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if "//" in line:
                line = line.split("//")[0]

            if ":" in line:
                label, instruction = line.split(":", 1)
                self.labels[label.strip()] = len(self.instructions)
                line = instruction.strip()

            if line:
                line = line.replace(",", "")
                self.instructions.append(line.split())

    def execute(self):
        while self.program_counter < len(self.instructions):
            instruction = self.instructions[self.program_counter]
            print(f"Executing: {' '.join(instruction)}, PC: {self.program_counter}")
            self.execute_instruction(instruction)
            print(
                f"After execution: PC: {self.program_counter}, Registers: {self.registers}, Flag: {self.comparison_flag}"
            )

    def execute_instruction(self, instruction):
        opcode = instruction[0]
        if opcode == "LOAD":
            self.load(instruction[1], instruction[2])
        elif opcode == "STORE":
            self.store(instruction[1], instruction[2])
        elif opcode in ["ADD", "SUB", "MUL", "DIV"]:
            self.arithmetic(opcode, instruction[1], instruction[2], instruction[3])
        elif opcode == "CMP":
            self.compare(instruction[1], instruction[2])
        elif opcode in ["JL", "JG", "JZ", "JMP"]:
            self.jump(opcode, instruction[1])
            return
        elif opcode == "PUSH":
            self.push(instruction[1])
        elif opcode == "POP":
            self.pop(instruction[1])
        else:
            raise ValueError(f"Unknown instruction: {opcode}")
        self.program_counter += 1

    def load(self, register, value):
        self.registers[register] = self.get_value(value)

    def store(self, register, value):
        self.set_value(value, self.registers[register])

    def arithmetic(self, operation, dest, src1, src2):
        val1 = self.registers[src1]
        val2 = self.registers[src2] if src2[0] == "R" else int(src2)
        if operation == "ADD":
            result = val1 + val2
        elif operation == "SUB":
            result = val1 - val2
        elif operation == "MUL":
            result = val1 * val2
        elif operation == "DIV":
            if val2 == 0:
                raise ValueError("Division by zero")
            result = val1 // val2
        self.registers[dest] = result

    def compare(self, reg1, reg2):
        val1 = self.registers[reg1]
        val2 = self.registers[reg2]
        if val1 < val2:
            self.comparison_flag = "L"
        elif val1 > val2:
            self.comparison_flag = "G"
        else:
            self.comparison_flag = "Z"

    def jump(self, condition, label):
        should_jump = False
        if condition == "JMP":
            should_jump = True
        elif condition == "JL" and self.comparison_flag == "L":
            should_jump = True
        elif condition == "JG" and self.comparison_flag == "G":
            should_jump = True
        elif condition == "JZ" and self.comparison_flag == "Z":
            should_jump = True

        if should_jump:
            if label not in self.labels:
                raise ValueError(f"Undefined label: {label}")
            self.program_counter = self.labels[label]
        else:
            self.program_counter += 1

    def push(self, register):
        self.stack.append(self.registers[register])

    def pop(self, register):
        if not self.stack:
            raise ValueError("Stack underflow")
        self.registers[register] = self.stack.pop()

    def get_value(self, operand):
        if operand.startswith("@"):
            return self.memory[int(operand[1:])]
        elif operand.startswith("R"):
            return self.registers[operand]
        else:
            return int(operand)

    def set_value(self, operand, value):
        if operand.startswith("@R"):
            self.memory[self.registers[operand[1:]]] = value
        elif operand.startswith("@"):
            self.memory[int(operand[1:])] = value
        elif operand.startswith("R"):
            self.registers[operand] = value
        else:
            raise ValueError(f"Invalid destination: {operand}")

    def print_state(self):
        print("Registers:", self.registers)
        print("Stack:", self.stack)
        print("Memory (first 10 elements):", self.memory[:10])

    def load_program_from_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        with open(filename, "r") as file:
            code = file.read()

        self.parse(code)
        print(f"Program loaded from {filename}")


def main():
    interpreter = BasicASMInterpreter()
    filename = (
        "factorial.asm"  # input("Enter the name of the BasicASM file to execute: ")
    )

    try:
        interpreter.load_program_from_file(filename)
        interpreter.execute()
        interpreter.print_state()

    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
