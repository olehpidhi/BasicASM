import os
import json
import argparse


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

    def execute_step(self):
        if self.program_counter >= len(self.instructions):
            return False

        instruction = self.instructions[self.program_counter]
        print(f"Executing: {' '.join(instruction)}, PC: {self.program_counter}")
        self.execute_instruction(instruction)
        print(
            f"After execution: PC: {self.program_counter}, Registers: {self.registers}, Flag: {self.comparison_flag}"
        )
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
            return True
        return False

    def push(self, register):
        self.stack.append(self.registers[register])

    def pop(self, register):
        if not self.stack:
            raise ValueError("Stack underflow")
        self.registers[register] = self.stack.pop()

    def get_value(self, operand):
        if operand.startswith("@R"):
            return self.memory[self.registers[operand[1:]]]
        elif operand.startswith("@"):
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


def main():
    parser = argparse.ArgumentParser(description="BasicASM Interpreter")
    parser.add_argument("filename", help="The BasicASM file to execute")
    parser.add_argument("-d", "--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "-b", "--breakpoints", type=int, nargs="*", help="Set initial breakpoints"
    )
    parser.add_argument("-m", "--memory", help="File to initialize memory from")

    args = parser.parse_args()

    interpreter = BasicASMInterpreter()

    interpreter.load_program_from_file(args.filename)

    if args.memory:
        interpreter.initialize_memory_from_file(args.memory)

    if args.breakpoints:
        for bp in args.breakpoints:
            interpreter.set_breakpoint(bp)

    if args.debug:
        while True:
            command = input().strip().split()
            if not command:
                continue

            if command[0] == "s":
                if not interpreter.execute_step():
                    print(json.dumps({"status": "ended"}))
                    break
                print(interpreter.get_state_json())
            elif command[0] == "c":
                if not interpreter.run_until_breakpoint():
                    print(json.dumps({"status": "ended"}))
                    break
                print(interpreter.get_state_json())
            elif command[0] == "b" and len(command) > 1:
                interpreter.set_breakpoint(int(command[1]))
                print(json.dumps({"status": "breakpoint_set", "line": int(command[1])}))
            elif command[0] == "r" and len(command) > 1:
                interpreter.remove_breakpoint(int(command[1]))
                print(
                    json.dumps(
                        {"status": "breakpoint_removed", "line": int(command[1])}
                    )
                )
            elif command[0] == "p":
                print(interpreter.get_state_json())
            elif command[0] == "q":
                print(json.dumps({"status": "quit"}))
                break
            else:
                print(json.dumps({"status": "error", "message": "Unknown command"}))
    else:
        interpreter.execute()
        print(interpreter.get_state_json())


if __name__ == "__main__":
    main()
