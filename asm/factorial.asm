LOAD R1 4
LOAD R2 1
LOAD R3 1 //Result

ADD R1 R1 1

Start:
CMP R2 R1
JZ End
MUL R3 R2 R3
ADD R2 R2 1
JMP Start

End: