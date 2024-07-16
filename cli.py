from interpreter import BasicASMInterpreter
import argparse
import json


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
