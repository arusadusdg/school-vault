---
id: canvas:assignment:53856
source: canvas
class: cs-hl
type: assignment
title: W16 - Dynamic Lists and Searching Algorithms
posted: '2026-09-04'
due: '2027-01-26'
updated: '2026-09-08T08:58:24Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53856
content_hash: 3bdede45646c1a3d
---

# W16 - Dynamic Lists and Searching Algorithms

**Topics:** dynamic Lists/ArrayLists, adding, removing and traversing elements, linear search, binary search, constructing and tracing search algorithms, and evaluating the efficiency and suitability of search techniques.

**Instructions**

* Answer all questions. **Total: 20 marks.**
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class. Java students may use ArrayList; Python students may use List.
* Where a question requires you to construct a search algorithm, do not use built-in search methods such as contains(), indexOf(), binarySearch(), in, index() or equivalent shortcuts unless explicitly permitted.
* For binary search questions, assume the data is sorted as shown. Your trace must record the changing search boundaries and midpoint.
* For construction questions, your code must work for all stated cases, including unsuccessful searches where required.
* Use appropriate indentation, meaningful identifiers, programming terminology and conventions.
* Evidence of any code used in this programming assignment must be copied and pasted directly into this Word document as editable text. Screenshots or images of code will not be accepted as evidence.
* If you develop or test your program in an IDE, copy the final relevant code from the IDE and paste it under the appropriate Answer heading in this document before submission.

**Questions**

(a) A dynamic list initially contains the following values:

[14, 21, 9, 35]

The program performs these operations in order:

* add 18 to the end of the list
* remove the element with value 21
* add 6 to the end of the list
* traverse the list and count how many values are greater than 15.

Trace these operations and state the final list and the final count. [3]

(b) Trace a linear search for target = 27 in the following list. Record each index examined and the value compared with the target. State the index returned by the search. [3]

data = [12, 5, 31, 18, 27, 44, 9]

(c) Trace a binary search for target = 42 in the following sorted array. For every iteration, record low, high, mid and the value at data[mid]. State the final index returned. [4]

data = [4, 11, 18, 25, 31, 37, 42, 49, 56, 63, 71]

(d) A school maintains a dynamic list of student identification numbers. Construct a program that:

* adds a new ID entered by the user to the list
* asks the user for an ID to remove
* removes that ID only if it exists
* traverses the updated list using your own linear search logic to locate a target ID entered by the user
* outputs the index of the target if found, otherwise outputs "Not found".

Do not use a built-in search method. [4]

(e) Compare linear search and binary search for data retrieval. Your answer must refer to the requirement for sorted data and to the number of comparisons that may be needed as the data set becomes large. [2]

(f) Evaluate the most suitable search method for each of the following scenarios. Support each recommendation with reasoning based on the characteristics of the data. [4]

Scenario 1: A help-desk application stores an unsorted dynamic list of active ticket IDs. Tickets are frequently added and removed, and the program occasionally searches for a specific ticket ID.

Scenario 2: A large, sorted and indexed list of customer names is searched many thousands of times each day to retrieve customer records.

**Total Marks: 20**
