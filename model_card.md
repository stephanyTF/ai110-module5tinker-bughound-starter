# BugHound Mini Model Card (Reflection)

Fill this out after you run BugHound in **both** modes (Heuristic and Gemini).

---

## 1) What is this system?

**Name:** BugHound  
**Purpose:** The BugHound reviews a Python snippet, propose a fix, and run reliability checks before suggesting whether the fix should be auto-applied.      
**Intended users:** Students learning agentic workflows and AI reliability concepts.


---

## 2) How does it work?

Describe the workflow in your own words (plan → analyze → act → test → reflect).  
Include what is done by heuristics vs what is done by Gemini (if enabled).

The workflow first starts by letting the user know its plan, then it goes to analyze the code by deteciting any issues (heuristics or LLM). After finding any issues, the BugHound proposes a fix or improved code. (for heuristics, there are pre-written suggestions for certain code issues, while Gemini may create a more tailored solution). It then checks its suggested code through the saftey check tests and deterimines whether its code is safe enough for the user to apply or needs additional human review. 

---

## 3) Inputs and outputs

**Inputs:**

- What kind of code snippets did you try?
   Correct code, mixed errors, commands that would affect the user's local env (e.g. os.system (cmd))
- What was the “shape” of the input (short scripts, functions, try/except blocks, etc.)?
   Short Scripts, functions meant to have a simple print output, try/except blocks

**Outputs:**

- What types of issues were detected?
    - logging / testing code w/ print statements
    - missing exception name from try / except block
    - division by zero
- What kinds of fixes were proposed? 
    - replacing print statements w/ logs
    - naming exceptions
    - checking values of inputs to avoid division by zero
- What did the risk report show?
    -  Risk level, Severity Score ( 0 - 100 where 100 is the most safe), and Auto Fix (bool value (yes or no))


---

## 4) Reliability and safety rules

List at least **two** reliability rules currently used in `assess_risk`. For each:

- What does the rule check?
    - Rule #1: Structural change checks how much of the code was changed based on its length difference
    - Rule #2: Issue severity based risk checks the severity score of the suggested code

- Why might that check matter for safety or correctness?
     - Rule #1: Structural change: Helps avoid implementing code that has been changed drastically in the case of affecting the user's original intention or project
     - Rule #2: Issue severity based risk helps measure how risky the new code is and whether the user should accept it or not
- What is a false positive this rule could cause?
     - Rule #1: Structural change: Eventhough the BugHound may insist that the new code is acceptable because there's not much change difference from the original, this could be false if the original was very incomplete or had unnecesary / wrong extra code. 
     - Rule #2: Issue severity based risk: Eventhough a suggested code could be cleared for a low or non existent severity score, this could be a false positive if the issue was mislabeled to be a low risk.
- What is a false negative this rule could miss?
    - Rule #1: Structural change:  Eventhough the BugHound may insist that the new code is not acceptable because of major changes, these structurla changes could be necessary for the code to work.
     - Rule #2: Issue severity based risk: Eventhough a suggested code could be flagged for a high severity score, this could be a false negative if the issue was mislabeled to be a high risk.

---

## 5) Observed failure modes

Provide at least **two** examples:

1. A time BugHound missed an issue it should have caught  
2. A time BugHound suggested a fix that felt risky, wrong, or unnecessary  

For each, include the snippet (or describe it) and what went wrong.

---

## 6) Heuristic vs Gemini comparison

Compare behavior across the two modes:

- What did Gemini detect that heuristics did not?
- What did heuristics catch consistently?
- How did the proposed fixes differ?
- Did the risk scorer agree with your intuition?

---

## 7) Human-in-the-loop decision

Describe one scenario where BugHound should **refuse** to auto-fix and require human review.

- What trigger would you add?
- Where would you implement it (risk_assessor vs agent workflow vs UI)?
- What message should the tool show the user?

---

## 8) Improvement idea

Propose one improvement that would make BugHound more reliable *without* making it dramatically more complex.

Examples:

- A better output format and parsing strategy
- A new guardrail rule + test
- A more careful “minimal diff” policy
- Better detection of changes that alter behavior

Write your idea clearly and briefly.
