import os
import json


class BasicASMInterpreter:
    def __init__(self):
        self.memory = [0] * 100
        self.registers = {"R1": 0, "R2": 0, "R3": 0, "R4": 0}
        self.stack = []
        self.stack_size = 1000
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

    def execute_step(self):
        if self.program_counter >= len(self.instructions):
            return False

        instruction = self.instructions[self.program_counter]
        self.execute_instruction(instruction)
        return True

    def run_until_breakpoint(self):
        while self.program_counter < len(self.instructions):
            if self.program_counter in self.breakpoints:
                return True

            if not self.execute_step():
                return False

        return False

    def set_breakpoint(self, line_number):
        self.breakpoints.add(line_number)

    def remove_breakpoint(self, line_number):
        self.breakpoints.discard(line_number)

    def get_state(self):
        return {
            "program_counter": self.program_counter,
            "registers": self.registers,
            "memory": self.memory[:10],
            "stack": self.stack,
            "comparison_flag": self.comparison_flag,
        }

    def execute(self):
        while self.execute_step():
            pass

    def execute_instruction(self, instruction):
        opcode = instruction[0]
        jump_occurred = False
        if opcode == "LOAD":
            self.load(instruction[1], instruction[2])
        elif opcode == "STORE":
            self.store(instruction[1], instruction[2])
        elif opcode in ["ADD", "SUB", "MUL", "DIV"]:
            self.arithmetic(opcode, instruction[1], instruction[2], instruction[3])
        elif opcode == "CMP":
            self.compare(instruction[1], instruction[2])
        elif opcode in ["JL", "JG", "JZ", "JMP"]:
            jump_occurred = self.jump(opcode, instruction[1])
        elif opcode == "PUSH":
            self.push(instruction[1])
        elif opcode == "POP":
            self.pop(instruction[1])
        else:
            raise ValueError(f"Unknown instruction: {opcode}")

        if not jump_occurred:
            self.program_counter += 1

        return jump_occurred

    def load(self, register, value):
        self.write_register(register, self.get_value(value))

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
        val2 = self.get_value(reg2)
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
                raise IndexError(f"Undefined label: {label}")
            self.program_counter = self.labels[label]
            return True
        return False

    def push(self, register):
        if len(self.stack) >= self.stack_size:
            raise IndexError("Stack overflow")
        self.stack.append(self.registers[register])

    def pop(self, register):
        if not self.stack:
            raise ValueError("Stack underflow")
        self.registers[register] = self.stack.pop()

    def read_from_memory(self, address):
        if address < 0 or address >= len(self.memory):
            raise IndexError(f"Memory access out of bounds: {address}")
        return self.memory[address]

    def read_register(self, register):
        if register not in self.registers:
            raise KeyError(f"Invalid register: {register}")
        return self.registers[register]

    def get_value(self, operand):
        if operand.startswith("@R"):
            register = operand[1:]
            address = self.read_register(register)
            return self.read_from_memory(address)
        elif operand.startswith("R"):
            return self.read_register(operand)
        elif operand.startswith("@"):
            address = int(operand[1:])
            return self.read_from_memory(address)
        else:
            return int(operand)

    def write_memory(self, address, value):
        if address < 0 or address >= len(self.memory):
            raise IndexError(f"Memory access out of bounds: {address}")
        self.memory[address] = value

    def write_register(self, register, value):
        if register not in self.registers:
            raise KeyError(f"Invalid register: {register}")
        self.registers[register] = value

    def set_value(self, operand, value):
        if operand.startswith("@R"):
            register = operand[1:]
            address = self.read_register(register)
            self.write_memory(address, value)
        elif operand.startswith("@"):
            address = int(operand[1:])
            self.write_memory(address, value)
        elif operand.startswith("R"):
            self.write_register(operand, value)
        else:
            raise ValueError(f"Invalid destination: {operand}")

    def load_program_from_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        with open(filename, "r") as file:
            code = file.read()

        self.parse(code)
        print(f"Program loaded from {filename}")

    def get_state_json(self):
        return json.dumps(
            {
                "program_counter": self.program_counter,
                "registers": self.registers,
                "memory": self.memory,
                "stack": self.stack,
                "comparison_flag": self.comparison_flag,
                "current_instruction": (
                    " ".join(self.instructions[self.program_counter])
                    if self.program_counter < len(self.instructions)
                    else "END"
                ),
            }
        )

    def initialize_memory_from_file(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")

        with open(filename, "r") as file:
            for i, line in enumerate(file):
                try:
                    value = int(line.strip())
                    self.memory[i] = value
                except ValueError:
                    print(f"Warning: Invalid integer on line {i+1}. Skipping.")
                except IndexError:
                    print(
                        f"Warning: Memory initialization stopped at address {i}. File contains more values than available memory."
                    )
                    break

        print(f"Memory initialized from {filename}")
