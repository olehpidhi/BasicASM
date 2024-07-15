LOAD R1, @0
LOAD R2, 0
LOAD R4, 1  // Result will be here
Start:
CMP R1, R2
JZ End
LOAD R3, 2
MUL R4, R4, R3
LOAD R3, 1
SUB R1, R1, R3
JMP Start
End: