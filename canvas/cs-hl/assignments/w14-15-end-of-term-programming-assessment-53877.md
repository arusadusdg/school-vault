---
id: canvas:assignment:53877
source: canvas
class: cs-hl
type: assignment
title: W14/15 - End-of-Term Programming Assessment
posted: '2026-09-04'
due: '2027-01-19'
updated: '2026-09-08T08:58:24Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53877
content_hash: 4024622afba738ff
---

# W14/15 - End-of-Term Programming Assessment

**Primary focus:** static and dynamic data structures, one-dimensional arrays, array manipulation, selection, loops, tracing, debugging and program construction.

**Assessment Instructions**

* Complete all sections of this assessment.
* This assessment is released in Week 14 and must be submitted by the end of Week 15.
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class, or clear pseudocode where appropriate.
* Assume zero-based indexing for arrays unless otherwise stated.
* Show all required tracing. Final outputs without evidence of tracing may not receive full marks.
* For construction questions, your algorithm must satisfy every stated requirement and work for boundary and exceptional cases.
* Do not use built-in functions such as sum(), max(), min() or equivalent shortcuts where the question requires explicit traversal, accumulation or comparison logic.
* Use appropriate indentation, meaningful identifiers, programming terminology and conventions.
* Total: 30 marks.

**Section A: Data Structures [5 marks]**

(a) Compare static and dynamic data structures. Your answer should refer to how memory/size is managed and the implications for storing a changing amount of data. [3]

(b) A school knows that exactly 12 monthly attendance percentages will be stored for each student. Another system must store an unknown number of support requests that may be added and removed throughout the day. Identify the more appropriate type of data structure for each situation and justify one of your choices. [2]

**Section B: Trace and Analyse [6 marks]**

(c) Trace the following algorithm. Show the values of i, total and selected after each iteration, then state the final outputs. [3]

values = [18, 7, 24, 11, 30, 5]  
 total = 0  
 selected = 0  
  
 FOR i = 0 TO 5  
 IF values[i] MOD 2 == 0 AND values[i] > 15  
      total = total + values[i]  
      selected = selected + 1  
 ELSE IF values[i] < 10  
      total = total - values[i]  
 END IF  
 END FOR  
  
 OUTPUT total  
 OUTPUT selected

(d) The following algorithm is intended to replace every negative value in readings with 0 and count how many replacements were made.

readings = [4, -2, 7, -5, 3]  
 changed = 0  
  
 FOR i = 0 TO 5  
 IF readings[i] < 0  
      readings[i] = 0  
 END IF  
 changed = changed + 1  
 END FOR  
  
 OUTPUT readings  
 OUTPUT changed

Analyse the algorithm and explain two logical errors. Construct the corrections required. [3]

**Section C: Debug and Improve [5 marks]**

(e) A program should calculate the average of all scores that are at least 50. If no score meets the condition, it should output "No qualifying scores".

scores = [45, 70, 82, 39, 50]  
 total = 0  
 count = 0  
  
 FOR i = 0 TO 4  
 IF scores[i] > 50  
      count = count + 1  
 END IF  
 END FOR  
 average = total / count  
 OUTPUT average

Analyse the algorithm and construct an improved version that meets all stated requirements. [5]

**Section D: Program Construction [8 marks]**

(f) A school stores the percentage scores of 10 students in a one-dimensional array called scores.

Construct an algorithm that traverses the array once and:

* counts the number of scores below 50
* calculates the total of all scores from 50 to 79 inclusive
* identifies the highest score without using a built-in maximum function
* identifies the index of the highest score
* replaces every score below 40 with 40
* outputs the count below 50, the total for scores from 50 to 79, the highest score, its index, and the modified array.

Assume that scores contains exactly 10 values and at least one value. [8]

**Section E: Unfamiliar Problem [6 marks]**

(g) A community library records the number of books borrowed each day in a one-dimensional array. The number of recorded days is fixed for the reporting period.

Construct an algorithm that:

* traverses all recorded values
* counts the number of days with zero loans
* calculates the total number of loans
* identifies the first day index on which the maximum number of loans occurred, without using a built-in maximum function
* outputs "Investigate low activity" if at least half of the recorded days have fewer than 5 loans.

Your solution must work for any non-empty array of daily loan values. [4]

(h) Justify two design decisions you made in part (g), referring to the choice of loop, initialization, conditions, counters, accumulators or comparison logic. [2]

**Total Marks: 30**
