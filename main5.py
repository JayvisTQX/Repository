import csv

# Analyze student_grades.csv
# Use map() to convert strings to integers
with open("/home/codespace/python-langapp-curriculum/5_FileIO/data/student_grades.csv", "r") as file:
    reader = csv.reader(file)
    grades = []
    for row in reader:
        grade = list(map(int, row[1])) # Convert the grade from string to integer
        grades.append(grade)