from collections import Counter
# This file contains the code for analyzing words in words_analyser.ipynb
# Verify if there are duplicated words in words.txt
with open("/home/codespace/python-langapp-curriculum/5_FileIO/data/words.txt", "r") as file:
    words = file.read() # assign variable to read words.txt
    word_list = words.splitlines() # splitlines() method splits the string into a list of lines, using the newline character as the delimiter
    unique_words = set(word_list) # set() is a built-in function that creates a set object, which is an unordered collection of unique elements. By converting the list of words into a set, we can easily determine the number of unique words in the file.
    if len(word_list) == len(unique_words): # If the length of the original list of words is equal to the length of the set of unique words, it means there are no duplicated words in the file. If they are not equal, it means there are duplicated words.
        print("No duplicated words.")
    else:
        print("There are duplicated words.")

# Verify if there are duplicated words in words.txt and list them
with open("/home/codespace/python-langapp-curriculum/5_FileIO/data/words.txt", "r") as file:
    words = file.read()
    word_list = words.splitlines()
    
    # Count occurrences of each word
    word_count = Counter(word_list) # Counter is a subclass of dict that helps count hashable objects. It takes an iterable (like a list) and returns a dictionary-like object where the keys are the unique elements from the iterable and the values are the counts of those elements in the iterable. In this case, it counts how many times each word appears in the word_list.
    
    # Find words with duplicates
    # dictionary comprehension - give me the "word: count" - if condition is met, loop the for loop
    duplicated_words = {word: count for word, count in word_count.items() if count > 1} # This is a dictionary comprehension that creates a new dictionary called duplicated_words. It iterates over the items in word_count (which are key-value pairs of words and their counts) and includes only those pairs where the count is greater than 1, meaning the word appears more than once in the original list.
    
    if len(duplicated_words) == 0:
        print("No duplicated words.")
    else:
        print(f"Found {len(duplicated_words)} duplicated words:\n")
        for word, count in sorted(duplicated_words.items()): # This loop iterates over the items in the duplicated_words dictionary, sorted by the word (the key). The sorted() function sorts the items based on the keys by default. For each word and its corresponding count, it prints a formatted string that shows the word and how many times it appears in the file.
            print(f"  '{word}' appears {count} times")
    print(word_count) # assign 