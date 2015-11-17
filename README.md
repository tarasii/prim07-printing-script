# prim07-printing-script

Prim07 is russian fiscal printer.
Prim07 has two ways of printing: with his commands and in ND77 printer mode.
Prim07 with his commands can print in fiscal mode and in random document mode.

commands:
1: 70 - turn on ND77 printer mode
ESC ESC - get out of printing mode

2: random document mode
50 - open random documet
51 - add line
56 - add multiline
52 - close random document and print

3: fiscal mode
10 - open bill
11 - add line
12 - bill total
13 - payment
14 - close bill and print

ESC = 1Bh
FS  = 1Сh
STX = 02h
ETX = 03h

Command format:
STX+pass+n+cmd+FS+...+FS+ETX+BCC

n = 20h to FFh
pass = "AERF"
BCC = control summ
