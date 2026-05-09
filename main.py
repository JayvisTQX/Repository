# Method 1
# Opens words1.txt in read mode and assigns it to "file"
file = open("words1.txt", "r")
# Reads the first line with readline()
line = file.readline()
print(line)
# Closes the file; important to free up system resources
file.close()

# Method 2
# Assign "file"; file is automatically closed when the block ends; safer and preferred in python
with open("words1.txt", "r") as file:
    line = file.readline()
    print(line)

# read, readline, readlines to read one file
with open("words1.txt", "r") as file:
    whole_file = file.read()
    line = file.readline()
    lines = file.readlines()
    lined = file.write("This is a new line.\n")  # This will raise an error since the file is opened in read mode
    lined2 = file.writelines(["This is line 1.\n", "This is line 2.\n"])  # This will also raise an error
    print(whole_file)
    print(repr(whole_file))
    print(line)
    print(repr(line))
    print(lines)
    print(repr(lines))
    print(len(whole_file))