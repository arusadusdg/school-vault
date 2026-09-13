---
id: canvas:assignment:53862
source: canvas
class: cs-hl
type: assignment
title: W19 - Programming with Two-Dimensional Arrays
posted: '2026-09-04'
due: '2027-02-16'
updated: '2026-09-08T08:58:26Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53862
content_hash: 1e1168991ecaac89
---

# W19 - Programming with Two-Dimensional Arrays

**Syllabus alignment:** B2.2.2 Construct programs that apply arrays and Lists. This includes two-dimensional arrays in Java and two-dimensional Lists in Python. This content is common to both SL and HL, so all students complete the same questions.

**Topics:** structure of two-dimensional arrays/Lists, rows and columns, indexing, nested traversal, accessing and modifying elements, counters and accumulators in 2D data, conditional processing, debugging index logic, and scenario-based program construction.

**Instructions**

* Answer all questions. **Total: 20 marks.**
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class. Java students may use 2D arrays; Python students may use 2D Lists.
* Assume zero-based indexing unless otherwise stated.
* For tracing questions, show the relevant row index, column index and variable changes. A final answer without evidence of tracing may not receive full marks.
* For construction questions, your program must work for all stated cases and must correctly traverse the required rows and columns.
* Do not use built-in operations that replace the specific traversal, counting, total or maximum logic being assessed.
* Evidence of any code used in this programming assignment must be copied and pasted directly into this Word document as editable text. Screenshots or images of code will not be accepted as evidence.
* If you develop or test code in an IDE, copy the final relevant code and paste it under the appropriate Answer heading before submission.
* Use appropriate indentation, meaningful identifiers, programming terminology and conventions.

**Questions**

(a) Consider the following two-dimensional array:

values =  
 [ [4, 7, 2],  
   [9, 1, 6],  
   [5, 8, 3] ]

State the value stored at each of the following positions:

1. values[0][2]
2. values[2][1]
3. values[1][0]

Then state the number of rows and the number of columns in the array. [3]

(b) Trace the following algorithm using the 2D array shown. Show how total changes after every element is processed and state the final output. [3]

data =  
 [ [3, 8, 5],  
   [6, 2, 9] ]  
  
 total = 0  
 FOR row = 0 TO 1  
 FOR col = 0 TO 2  
      IF data[row][col] MOD 2 == 0  
          total = total + data[row][col]  
      ELSE  
          total = total - 1  
      END IF  
 END FOR  
 END FOR

OUTPUT total

(c) The following algorithm is intended to replace every negative value in a 3 x 4 matrix with 0 and count how many values were changed.

changed = 0  
 FOR row = 0 TO 3

FOR col = 0 TO 4  
      IF matrix[row][col] < 0  
          matrix[row][col] = 0  
      END IF  
      changed = changed + 1  
 END FOR

END FOR

Analyse the algorithm and identify two logical/indexing errors. Construct the required corrections. [4]

(d) A school stores test marks for 5 students across 4 assessments in a two-dimensional array called marks. Each row represents one student and each column represents one assessment.

Construct a program that:

* traverses the complete 5 x 4 array
* calculates the total marks for each student
* outputs each student's total after that student's row has been processed
* counts how many individual marks are below 50
* identifies the highest individual mark in the complete array without using a built-in maximum function
* outputs the below-50 count and the highest mark after the traversal is complete. [5]

Do not use a built-in operation that performs the complete counting or replacement task for you. [4]

(e) A cinema stores the number of seats booked in a 2D array called bookings. Rows represent screening times and columns represent days of the week.

Construct a program that:

* traverses the complete array
* calculates the total number of bookings
* counts how many cells contain 0 bookings
* identifies the row index with the greatest total bookings
* outputs the overall total, the number of zero-booking cells, and the row index with the greatest total.

If two rows have the same greatest total, output the index of the first such row. [5]

**Total: 20 marks**
