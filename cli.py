from interpreter import BasicASMInterpreter
from debugger import BasicASMDebugger
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

    if args.debug:
        debugger = BasicASMDebugger(interpreter)
        if args.breakpoints:
            for bp in args.breakpoints:
                debugger.set_breakpoint(bp)
        debugger.run()
        print(interpreter.get_state_json())
    else:
        interpreter.execute()
        print(interpreter.get_state_json())


if __name__ == "__main__":
    main()
