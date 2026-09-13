---
id: canvas:assignment:53852
source: canvas
class: cs-hl
type: assignment
title: W12 - Looping Structures - Tracing, Logic and Construction
posted: '2026-09-04'
due: '2026-12-08'
updated: '2026-09-08T08:58:23Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53852
content_hash: da13357b821882b8
---

# W12 - Looping Structures - Tracing, Logic and Construction

**Topics:** for loops, while loops, do-while loops, counted and conditional loops, Boolean and relational conditions, selection within loops, accumulators, counters, sentinel values, tracing, debugging and logic building.

**Instructions**

* Answer all questions. Total: 15 marks.
* Show the required tracing. A final output without evidence of tracing may not receive full marks.
* Use the programming language currently being studied in your class, or clear pseudocode where appropriate.
* For construction questions, your solution must work for all stated cases, not only a sample input.
* Pay careful attention to loop initialization, continuation/termination conditions, variable updates and boundary values.
* Where a scenario includes invalid input or a sentinel value, ensure that these are handled correctly.
* Use appropriate indentation, programming terminology and conventions.
* Your reasoning is important. Solutions that merely reproduce a familiar code pattern without satisfying the stated requirements will not receive full marks.

**Questions**

(a) Trace the following algorithm. Complete a trace showing the value of count and total after each iteration, then state the final output. [3]

total = 2  
 count = 1  
  
 WHILE count <= 4  
 IF count MOD 2 == 0  
      total = total + count \* 2  
 ELSE  
      total = total + count  
 END IF  
 count = count + 1  
 END WHILE  
  
 OUTPUT total

(b) Trace the following algorithm and determine the complete output sequence. Your working should show how both x and y change. [3]

x = 1  
 y = 8  
  
 FOR i = 1 TO 3  
 x = x \* 2  
 y = y - x  
 IF y > 2  
      OUTPUT x  
 ELSE  
      OUTPUT y  
 END IF  
 END FOR

(c) The following algorithm is intended to accept positive numbers, add them to total, and stop when 0 is entered.

total = 0  
 INPUT number  
 WHILE number >= 0  
 total = total + number  
 INPUT number  
 END WHILE  
 OUTPUT total

Analyse the algorithm and identify two logical problems or limitations that could cause it not to meet the stated objective in all cases. For each, suggest an appropriate correction. [3]

(d) A fitness application records daily step counts. The user enters one value at a time. The program must:

* stop when -1 is entered
* reject any other negative value and not include it in the calculations
* count the number of valid days entered
* calculate the total number of steps for valid days
* output the average number of steps only if at least one valid day was entered.
* Construct an algorithm using an appropriate looping structure that satisfies all requirements. [4]

(e) Justify why a conditional loop is more appropriate than a counted loop for the fitness application in part (d). [2]

**Total Marks: 15**
