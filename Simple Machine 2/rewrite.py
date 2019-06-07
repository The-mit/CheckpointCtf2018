# the stack extracted by hand
stack = [17, 108, 43, 69, 100, 40, 68, 116, 38, 97, 15, 102, 10, 102, 9, 91, 28, 82, 59, 87, 27, 43, 121, 62, 112, 57, 85, 57, 86, 4, 86, 57, 97, 26, 125, 28, 112, 22][::-1]
flag = ""
for i, c in enumerate(stack[:-1]):
	flag += chr(c ^ stack[i+1])

print flag
# flag{XoRRollINGR0LliNGRollinGR0lL!nG}
