---
id: canvas:assignment:53853
source: canvas
class: cs-hl
type: assignment
title: W13 - Selection, Loops and One-Dimensional Arrays
posted: '2026-09-04'
due: '2026-12-15'
updated: '2026-09-08T08:58:24Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53853
content_hash: 6955c06c8f87fc12
---

# W13 - Selection, Loops and One-Dimensional Arrays

**Topics:** selection and looping statements, one-dimensional arrays, array indexing and traversal, counters, accumulators, comparison logic, processing array elements, debugging array-based algorithms, and advantages and limitations of one-dimensional arrays.

**Instructions**

* Answer all questions. Total: 15 marks.
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class, or clear pseudocode where appropriate.
* Assume zero-based indexing for all arrays shown in this assessment unless otherwise stated.
* For tracing questions, show how relevant variables change during each iteration. A final output without evidence of tracing may not receive full marks.
* For construction questions, your program must work for all stated cases and must traverse the array correctly.
* Do not use built-in functions such as sum(), max(), min() or equivalent shortcuts when the question requires you to demonstrate traversal or comparison logic.
* Use appropriate indentation, programming terminology and conventions.

**Questions**

(a) Trace the following algorithm. Show the values of i, total and count after each iteration, then state the final two outputs. [3]

scores = [72, 45, 88, 51, 39]  
 total = 0  
 count = 0  
  
 FOR i = 0 TO 4  
 IF scores[i] >= 50  
      total = total + scores[i]  
      count = count + 1  
 ELSE  
      total = total - 5  
 END IF  
 END FOR  
  
 OUTPUT total  
 OUTPUT count

(b) The following algorithm is intended to calculate the total of all values stored in the array.

values = [12, 9, 15, 7, 20]  
 total = 0  
  
 FOR i = 0 TO 5  
 total = 0  
 total = total + values[i]  
 END FOR  
  
 OUTPUT total

Explain two errors in the algorithm and construct the corrections needed so that the algorithm produces the correct total. [3]

(c) A school stores the attendance percentages of eight students in a one-dimensional array called attendance.

Construct an algorithm that traverses the complete array and:

* counts how many students have attendance below 75
* calculates the total attendance of students whose attendance is 75 or above
* identifies the highest attendance value without using a built-in max() function or equivalent
* outputs the three results.

Assume the array contains at least one value. [4]

(d) An array called requests stores the number of technical-support requests received on each of seven days.

Construct an algorithm that traverses the array and:

* calculates the total number of requests
* counts the number of days on which requests were greater than 50
* outputs "Review staffing" only if at least three days had more than 50 requests.

Do not use built-in aggregation functions. [3]

(e) Explain one advantage and one limitation of using a one-dimensional array to store the attendance percentages in part (c). [2]

**Total Marks: 15**
