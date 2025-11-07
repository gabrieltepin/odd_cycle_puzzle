# Odd-Length Exchanges in ABO-Only Kidney Exchange

### A Feasibility Puzzle for Undergraduate Operations Research Courses  
Companion repository for the paper **"Odd-Length Exchanges in ABO-Only Kidney Exchange"**, submitted to *INFORMS Transactions on Education*.

---

## 🧩 Overview

This repository accompanies the cmain ideas presented in our paper, which explores a fundamental modeling question in kidney exchange programs (KEPs):

> **Can odd-length cycles—such as three-way exchanges—occur when every donor–recipient pair is internally incompatible and compatibility is defined solely by ABO blood type?**

Unlike most optimization exercises that seek the *best* solution, this activity focuses on **feasibility**—whether a solution exists at all.  
Students are guided to translate domain rules into binary variables and linear constraints, reason about infeasibility, and connect algebraic simplifications with medical and operational context.

---

## 📘 Structure and Pedagogical Goal

The repository illustrates how a short **mixed-integer feasibility model** can be used to demonstrate the concept of structural impossibility in matching systems.

The code implements:
1. **Base formulation** – mirrors the mathematical model described in the paper:
   - Assignment constraints (each donor and recipient receives one blood-type label)
   - Internal incompatibility (within-pair constraints)
   - Cycle implications (across pairs, using modular indexing)
2. **Variable fixings** – simple algebraic deductions that shrink the model and reveal infeasibility sources *before solving*.
3. **Reduced formulation** – collapses the model to two remaining types (A and B) after fixings.
4. **Solution routine** – builds and solves the model in Python with [Gurobi](https://www.gurobi.com/), producing either:
   - A feasible ABO assignment for the cycle, or  
   - A solver-issued **certificate of infeasibility** (via Gurobi’s IIS analysis).

These elements make the exercise ideal for teaching:
- Feasibility vs. optimality in modeling,  
- The logic of constraint propagation and variable fixings, and  
- How domain rules (e.g., medical compatibility) map directly to binary constraints.

---

## 🧮 Mathematical Formulation

The model defines binary variables  
`x[r_i, b]` = 1 if recipient *i* is assigned blood type *b*, and  
`y[d_i, b]` = 1 if donor *i* is assigned blood type *b*,  
for each pair \( i \in \{1,2,3\} \) and \( b \in \{A, B, O, AB\} \).

Constraint blocks include:
- **Assignment:** Each person has exactly one blood-type label.  
- **Internal incompatibility:** Donor and recipient within the same pair cannot be compatible.  
- **Cycle implications:** Donor \( d_i \) must be compatible with the next recipient \( r_j \), where \( j = 1 + (i \bmod 3) \).  
- **Binary domains:** All decision variables are binary.

The formulation generalizes naturally to any odd cycle of size ≥ 5 using the same modular structure.

---

## 🧠 Key Insight: Simplifying by Fixings

Before solving, several variables can be fixed algebraically:
- \( y_{d_i,O} = 0 \)
- \( x_{r_i,AB} = 0 \)
- \( y_{d_i,AB} = 0 \)
- \( x_{r_i,O} = 0 \)

These fixings reduce the problem to a two-type (A/B) world, showing that the feasibility of odd-length exchanges collapses under ABO-only assumptions.  
This reasoning demonstrates infeasibility **without needing the solver**—a powerful teaching moment in presolve logic.

---

## 💻 Repository Contents

```
odd_cycle_puzzle/
│
├── main_base_formulation.py # Implements the 4-type (A,B,O,AB) base feasibility model
├── main_with_fixings.py # Implements algebraic fixings before solving
├── main_reduced_formulation.py # Implements reduced 2-type (A,B) model
├── example_notebook.ipynb # Interactive walkthrough and discussion cells
├── README.md # This documentation file
└── requirements.txt # Dependencies (gurobipy, etc.)
```

## 🚀 How to Run

You can explore a **live interactive demo** of the puzzle directly in your browser — no installation required.

🎯 **Try it here:**  
👉 [**Blood-Type Exchange Dashboard**](https://gabrieltepin.github.io/odd_cycle_puzzle/)  

This GitHub Pages site lets students:
- Select donor and recipient blood types for each of the three pairs.
- Visualize the directed cycle structure.
- Check feasibility instantly based on ABO-only compatibility logic.  

The dashboard runs **fully client-side** (in JavaScript) and mirrors the logic of the Python+Gurobi formulation used in the paper.  
It provides an accessible, hands-on way for students to test combinations and reason about feasibility before examining the algebraic model.

### 1. Clone the repository
```bash
git clone https://github.com/gabrieltepin/odd_cycle_puzzle.git

cd odd_cycle_puzzle

pip install -r requirements.txt

python main.py
```

## Interpretable results

Valid instance: The script prints 
✅ Valid solution a blood-type assignment for each donor–recipient pair.

Invalid instance: The script prints
❌ Invalid solution (no odd-length ABO-only cycle exists)
and exports an IIS file infeasible_constraints.ilp. Try to run the 
👉 [**base formulation model**](https://github.com/gabrieltepin/odd_cycle_puzzle/blob/master/main.py)  

## Classroom Use

The model solves instantly on a standard laptop.
Students can experiment with: 

- changing the number of pairs 

```python
pairs = [1, 2, 3, 4, 5, ...]
```
- Pre-fixing donor or recipient types
- Comparing constraint counts before and after fixings
- Instru