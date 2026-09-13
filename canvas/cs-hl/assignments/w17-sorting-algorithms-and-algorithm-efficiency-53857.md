---
id: canvas:assignment:53857
source: canvas
class: cs-hl
type: assignment
title: W17 - Sorting Algorithms and Algorithm Efficiency
posted: '2026-09-04'
due: '2027-02-02'
updated: '2026-09-08T08:58:25Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53857
content_hash: 9973544245cbb8fe
---

# W17 - Sorting Algorithms and Algorithm Efficiency

**Topics:** bubble sort, selection sort, tracing sorting algorithms, constructing sorting algorithms, time and space complexity, Big O notation, scalability, efficiency, and algorithm selection.

**Instructions**

* Answer all questions. **Total: 20 marks.**
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class, or clear pseudocode where appropriate.
* For sorting traces, show the state of the data after each required pass. A final sorted list without the required trace will not receive full marks.
* For construction questions, do not use built-in sorting methods such as sort(), sorted(), Arrays.sort(), Collections.sort() or equivalent shortcuts.
* Where efficiency is discussed, distinguish between time complexity and space complexity and use Big O notation where required.
* Evidence of any code used in this programming assignment must be copied and pasted directly into this Word document as editable text. Screenshots or images of code will not be accepted as evidence.
* If code is developed or tested in an IDE, copy the final relevant code and paste it under the appropriate Answer heading before submission.
* Use appropriate indentation, meaningful identifiers, programming terminology and conventions.

**Questions**

(a) A small delivery company records the number of minutes taken for six deliveries:

[29, 12, 41, 7, 18, 33]

The company wants the values in ascending order. Trace bubble sort on this data. Show the complete array after each full pass and indicate when no further swaps are required. [4]

(b) A game stores six player scores:

[46, 15, 38, 22, 51, 9]

Trace selection sort to arrange the scores in ascending order. For each pass, identify the position being filled, the minimum value found in the unsorted portion, and the array after the swap. [4]

(c) The following algorithm is intended to implement bubble sort in ascending order, but it contains errors.

n = LENGTH(values)  
 FOR pass = 0 TO n - 1  
 FOR i = 0 TO n - 1  
      IF values[i] < values[i + 1]  
          SWAP values[i], values[i + 1]  
      END IF  
 END FOR  
 END FOR

Analyse the algorithm and construct a corrected version that sorts the array in ascending order without accessing an invalid index. Your corrected version should also avoid comparisons that are known to be unnecessary after completed passes. [4]

(d) Explain the time complexity and auxiliary space complexity of the standard in-place bubble sort and selection sort algorithms studied in this course. Use Big O notation and relate the notation to how the amount of work changes as n increases. [3]

(e) Evaluate the suitability of bubble sort and selection sort in each scenario below. [3]

Scenario 1: A classroom application occasionally sorts 20 quiz scores. The data may already be almost sorted, and the implementation of bubble sort stops early if a complete pass makes no swaps.

Scenario 2: A small embedded device sorts 200 values in memory. Writing/swapping stored values is relatively costly, but comparisons are less costly.

For each scenario, recommend the more suitable of the two algorithms and support the recommendation using relevant characteristics of the algorithms.

(f) A developer proposes using selection sort to repeatedly sort a collection that may grow from 100 records to 1,000,000 records. Justify why the Big O time complexity should influence the developer's decision about whether this algorithm will scale appropriately. [2]

**Total: 20 marks**
