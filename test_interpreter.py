import unittest
from interpreter import BasicASMInterpreter


class TestBasicASMInterpreter(unittest.TestCase):

    def setUp(self):
        self.interpreter = BasicASMInterpreter()

    def test_memory_out_of_bounds_access(self):
        code = """
        LOAD R1, @1000
        """
        self.interpreter.parse(code)
        with self.assertRaises(IndexError):
            self.interpreter.execute()

    def test_memory_out_of_bounds_store(self):
        code = """
        LOAD R1, 42
        STORE R1, @1000
        """
        self.interpreter.parse(code)
        with self.assertRaises(IndexError):
            self.interpreter.execute()

    def test_division_by_zero(self):
        code = """
        LOAD R1, 10
        LOAD R2, 0
        DIV R3, R1, R2
        """
        self.interpreter.parse(code)
        with self.assertRaises(ValueError):
            self.interpreter.execute()

    def test_invalid_instruction(self):
        code = """
        INVALID R1, R2
        """
        self.interpreter.parse(code)
        with self.assertRaises(ValueError):
            self.interpreter.execute()

    def test_jump_to_invalid_label(self):
        code = """
        JMP NonExistentLabel
        """
        self.interpreter.parse(code)
        with self.assertRaises(IndexError):
            self.interpreter.execute()

    def test_stack_underflow(self):
        code = """
        POP R1
        """
        self.interpreter.parse(code)
        with self.assertRaises(ValueError):
            self.interpreter.execute()

    def test_stack_overflow(self):
        code = "PUSH R1\n" * 1001  # Assuming 1000 is the maximum stack size
        self.interpreter.parse(code)
        with self.assertRaises(IndexError):
            self.interpreter.execute()

    def test_invalid_register(self):
        code = """
        LOAD R5, 10
        """
        self.interpreter.parse(code)
        with self.assertRaises(KeyError):
            self.interpreter.execute()

    def test_program_counter_out_of_bounds(self):
        code = """
        JMP 100
        """
        self.interpreter.parse(code)
        with self.assertRaises(IndexError):
            self.interpreter.execute()

    def test_unconditional_jump(self):
        code = """
        LOAD R1, 0
        JMP SkipIncrement
        LOAD R1, 1
        SkipIncrement:
        LOAD R2, 42
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R1"], 0)
        self.assertEqual(self.interpreter.registers["R2"], 42)

    def test_jump_less_than(self):
        code = """
        LOAD R1, 5
        LOAD R2, 10
        CMP R1, R2
        JL LessThan
        LOAD R3, 0
        JMP End
        LessThan:
        LOAD R3, 1
        End:
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R3"], 1)

    def test_jump_greater_than(self):
        code = """
        LOAD R1, 15
        LOAD R2, 10
        CMP R1, R2
        JG GreaterThan
        LOAD R3, 0
        JMP End
        GreaterThan:
        LOAD R3, 1
        End:
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R3"], 1)

    def test_jump_equal(self):
        code = """
        LOAD R1, 10
        LOAD R2, 10
        CMP R1, R2
        JZ Equal
        LOAD R3, 0
        JMP End
        Equal:
        LOAD R3, 1
        End:
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R3"], 1)

    def test_jump_not_taken(self):
        code = """
        LOAD R1, 10
        LOAD R2, 5
        CMP R1, R2
        JL LessThan
        LOAD R3, 1
        JMP End
        LessThan:
        LOAD R3, 0
        End:
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R3"], 1)

    def test_multiple_jumps(self):
        code = """
        LOAD R1, 0
        Start:
        ADD R1, R1, 1
        CMP R1, 5
        JL Start
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R1"], 5)

    def test_jump_to_earlier_instruction(self):
        code = """
        LOAD R1, 0
        LOAD R2, 5
        Loop:
        ADD R1, R1, 1
        CMP R1, R2
        JL Loop
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R1"], 5)

    def test_nested_jumps(self):
        code = """
        LOAD R1, 0
        LOAD R2, 0
        OuterLoop:
        LOAD R3, 0
        InnerLoop:
        ADD R3, R3, 1
        CMP R3, 3
        JL InnerLoop
        ADD R2, R2, 1
        CMP R2, 2
        JL OuterLoop
        ADD R1, R2, R3
        """
        self.interpreter.parse(code)
        self.interpreter.execute()
        self.assertEqual(self.interpreter.registers["R1"], 5)
        self.assertEqual(self.interpreter.registers["R2"], 2)
        self.assertEqual(self.interpreter.registers["R3"], 3)


if __name__ == "__main__":
    unittest.main()
