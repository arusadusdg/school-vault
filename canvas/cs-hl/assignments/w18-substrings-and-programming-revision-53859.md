---
id: canvas:assignment:53859
source: canvas
class: cs-hl
type: assignment
title: W18 - Substrings and Programming Revision
posted: '2026-09-04'
due: '2027-02-09'
updated: '2026-09-08T08:58:25Z'
url: https://pamojaeducation.instructure.com/courses/734/assignments/53859
content_hash: 3dd87b45462fae4a
---

# W18 - Substrings and Programming Revision

**Topics:** extracting and manipulating substrings, altering, concatenating and replacing string content, selection, loops, one-dimensional arrays/Lists, traversal, linear search, counters, accumulators and cumulative programming problem solving.

**Instructions**

* Answer all questions. **Total: 20 marks.**
* Read each question carefully and respond according to the IB command term used.
* Use the programming language currently being studied in your class. Java or Python solutions are acceptable where appropriate.
* Because Java substring methods and Python slicing use different syntax, marks are awarded for correct extraction logic and output rather than requiring identical syntax across languages.
* Where a question requires traversal or search logic, do not replace the required algorithm with a built-in method that performs the whole task automatically.
* For construction questions, your solution must work for all stated cases, not only the sample data.
* Evidence of any code used in this programming assignment must be copied and pasted directly into this Word document as editable text. Screenshots or images of code will not be accepted as evidence.
* If you develop or test code in an IDE, copy the final relevant code and paste it under the appropriate Answer heading in this document before submission.
* Use appropriate indentation, meaningful identifiers, programming terminology and conventions.

**Questions**

(a) A school stores student identifiers in the following fixed format:

2027-ROY-MARTIN-CS

The first four characters represent the graduation year, characters 5 to 7 represent the surname code, characters 9 to 14 represent the first name, and the final two characters represent the subject code.

Trace the required substring extractions and state the four resulting values. [3]

(b) A username is stored in the format:

surname.firstname.year

For example:

 roy.martin.2027

Construct a program that extracts the surname, first name and year into separate variables, then constructs and outputs a new identifier in the format:

YEAR-SURNAME-FIRSTNAME

For the example above, the output should be:

2027-ROY-MARTIN

You may use appropriate substring/slicing and case-conversion operations available in your programming language. [4]

(c) The following pseudocode is intended to replace every occurrence of a hyphen (-) in a product code with an underscore (\_) and then output the modified code.

code = "AB-24-CD-7"  
result = ""  
FOR i = 0 TO LENGTH(code)  
 IF code[i] == "-"  
      result = result + "\_"  
 ELSE  
      result = code[i]  
 END IF  
 END FOR  
  
 OUTPUT result

Explain two errors in this algorithm and construct the corrections required so that the correct output is produced. [3]

(d) A messaging application receives a string containing a message. Construct a program that:

* traverses every character in the string
* counts the number of spaces
* counts the number of digits (0 to 9)
* constructs a new string in which every space is replaced by an underscore
* outputs the two counts and the new string.

Do not use a built-in operation that performs the complete counting or replacement task for you. [4]

(e) A dynamic List/ArrayList contains usernames in the format surname.firstname.year. Construct a program that:

* asks the user to enter a target year
* traverses the complete list
* extracts the year from each username
* counts how many usernames belong to the target year
* asks the user to enter a target surname
* uses your own linear-search logic to find the first username with that surname
* outputs the matching username if found, otherwise outputs "Not found".

Do not use a built-in search method that replaces the required traversal/search logic. [4]

(f) Explain two design decisions that are important when constructing the program in part (e). Your answer may refer to substring boundaries, traversal, case handling, search termination, counters or unsuccessful searches. [2]

**Total: 20 marks**
