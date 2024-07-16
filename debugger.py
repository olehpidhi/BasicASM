import json
from interpreter import BasicASMInterpreter


class BasicASMDebugger:
    def __init__(self, interpreter: BasicASMInterpreter):
        self.interpreter: BasicASMInterpreter = interpreter
        self.running = True
        self.breakpoints = set()

    def run(self):
        print("Debug mode. Available commands:")
        print("  s: Step (execute one instruction)")
        print("  c: Continue (run until next breakpoint or end)")
        print("  b <line>: Set breakpoint at line")
        print("  r <line>: Remove breakpoint at line")
        print("  p: Print current state")
        print("  q: Quit debugger")

        while self.running:
            command = input("debug> ").strip().split()
            if not command:
                continue

            self.handle_command(command)

    def handle_command(self, command):
        cmd = command[0]
        if cmd == "s":
            self.step()
        elif cmd == "c":
            self.continue_execution()
        elif cmd == "b" and len(command) > 1:
            self.set_breakpoint(command[1])
        elif cmd == "r" and len(command) > 1:
            self.remove_breakpoint(command[1])
        elif cmd == "p":
            self.print_state()
        elif cmd == "q":
            self.quit()
        else:
            self.unknown_command()

    def step(self):
        if not self.interpreter.execute_step():
            print(json.dumps({"status": "ended"}))
            self.running = False
        else:
            print(self.interpreter.get_state_json())

    def continue_execution(self):
        while self.interpreter.program_counter not in self.breakpoints:
            if not self.interpreter.execute_step():
                print(json.dumps({"status": "ended"}))
                self.running = False
                return
        print(self.interpreter.get_state_json())

    def set_breakpoint(self, line):
        try:
            line_num = int(line)
            self.breakpoints.add(line_num)
            print(json.dumps({"status": "breakpoint_set", "line": line_num}))
        except ValueError:
            print(json.dumps({"status": "error", "message": "Invalid line number"}))

    def remove_breakpoint(self, line):
        try:
            line_num = int(line)
            self.breakpoints.discard(line_num)
            print(json.dumps({"status": "breakpoint_removed", "line": line_num}))
        except ValueError:
            print(json.dumps({"status": "error", "message": "Invalid line number"}))

    def print_state(self):
        print(self.interpreter.get_state_json())

    def quit(self):
        print(json.dumps({"status": "quit"}))
        self.running = False

    def unknown_command(self):
        print(json.dumps({"status": "error", "message": "Unknown command"}))
