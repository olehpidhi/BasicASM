// Initialize the first two Fibonacci numbers
LOAD R1, 0  // F(0) = 0
LOAD R2, 1  // F(1) = 1
LOAD R3, 0  // Memory address counter
LOAD R4, 10 // Number of Fibonacci numbers to calculate

// Store the first two numbers
STORE R1, @0
LOAD R3, 1
STORE R2, @1
LOAD R3, 2

// Main loop
Loop:
CMP R3, R4
JZ End     // If we've calculated 10 numbers, end the program

// Calculate next Fibonacci number
ADD R1, R1, R2  // R1 = R1 + R2 (new Fib number)
STORE R1, @R3   // Store the new number in memory
ADD R3, R3, 1   // Increment memory address
 
// Swap R1 and R2
LOAD R4, 0
ADD R4, R4, R2  // R4 = R2
LOAD R2, 0
ADD R2, R2, R1  // R2 = R1 (new Fib number)
LOAD R1, 0
ADD R1, R1, R4  // R1 = old R2

// Restore R4 and continue loop
LOAD R4, 10
JMP Loop

End: