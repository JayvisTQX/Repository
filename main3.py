# Write mode
# method 1
file = open("words1.txt", "w")
file.write("This is a new line.\n")
file.write("Hello, world!\n")
file.close()

# method 2
with open("words1.txt", "w") as file:
    file.write("Hi\n")
    file.write("Hello")