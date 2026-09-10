text = "hello @myVU students. welcome to 2026!"
print(text.upper())
print(text.lower())
"""no. of special characters"""
#reading and writing files
"""
4 modes of working with files
create - x
read - r
write - w
append - a
"""
# create a file
filename = "students.txt"
f = open(file=filename, mode="x")
f.close()
# writing to the file 
data  ={"id"=1, "name":"dave"}
with open(file=filename, mode="a")
f.writelines("\n")
# exception handling
numerator = float(input("enter the numerator:"))