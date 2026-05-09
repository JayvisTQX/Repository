import csv # The csv module in Python provides functionality to read from and write to CSV (Comma Separated Values) files. It allows you to easily handle CSV data, which is a common format for storing tabular data. The csv module provides classes and functions to read and write CSV files, making it easier to work with this type of data in Python.

data = [] # Empty list to store the data read from the CSV file

with open("/home/codespace/python-langapp-curriculum/5_FileIO/data/student_grades.csv") as file:
    reader = csv.reader(file) # csv.reader() is a function in the csv module that takes a file object as input and returns an iterator that produces the rows of the CSV file as lists. Each row in the CSV file is represented as a list of strings, where each string corresponds to a cell in that row. You can use this reader object to iterate through the rows of the CSV file and access the data contained within it.
    for i in reader: # This loop iterates over each row produced by the csv.reader() iterator. For each row (which is a list of strings), it appends that row to the data list. After this loop, the data list will contain all the rows from the CSV file, with each row represented as a list of strings.
        data.append(i) # This line appends the current row (represented as a list of strings) to the data list. After the loop completes, the data list will contain all the rows from the CSV file, allowing you to work with that data in your Python program.

print(data)

data = [
    ["Name", "Age"],
    ["Kevin", "Old"]
]

data2 = ["afsdgfsg", "dfaf"]

with open("/home/codespace/python-langapp-curriculum/5_FileIO/data/info.csv", "w") as file:
    write = csv.writer(file)
    # all at once
    write.writerows(data)
    # one by one
    for row in data:
        write.writerows(row)
        