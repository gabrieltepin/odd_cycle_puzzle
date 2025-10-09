import gurobipy as gp
from gurobipy import GRB

# --- Sets
pairs = [1, 2, 3]
types = ["O", "A", "B", "AB"]

# --- Model
m = gp.Model("blood_incompatibility")

# --- Variables
x = m.addVars(pairs, types, vtype=GRB.BINARY, name="x")  # recipient blood types
y = m.addVars(pairs, types, vtype=GRB.BINARY, name="y")  # donor blood types

# --- Constraints (1a), (1b)
for i in pairs:
    m.addConstr(gp.quicksum(x[i, t] for t in types) == 1, f"one_type_rec_{i}")
    m.addConstr(gp.quicksum(y[i, t] for t in types) == 1, f"one_type_don_{i}")

# --- Constraints (1c)-(1e): incompatibility per pair
for i in pairs:
    # (1c) Recipient O incompatible with donor A,B,AB    
    m.addConstr(y[i, "O"]  <= 1 - (x[i, "O"] + x[i, "A"]+ x[i, "B"]+ x[i, "AB"]), f"incomp_O_{i}")
    # (1d) Recipient A incompatible with donor B,AB
    m.addConstr(y[i, "A"]  <= 1 - (x[i, "A"] + x[i, "AB"]), f"incomp_A_{i}")
    # (1e) Recipient B incompatible with donor A,AB
    m.addConstr(y[i, "B"]  <= 1 - (x[i, "B"] + x[i, "AB"]), f"incomp_B_{i}")
    # (1f) Recipient AB incompatible with donor AB
    m.addConstr(y[i, "AB"]  <= 1 - (x[i, "AB"]), f"incomp_AB_{i}")

# --- Constraints (1f)-(1h): implication across consecutive pairs
for i in pairs:
    j = 1 + (i % 3)  # consecutive pair in cyclic order (1→2, 2→3, 3→1)
    # (1g)
    m.addConstr(y[i, "A"] <= x[j, "A"] + x[j, "AB"], f"imp_A_{i}")
    # (1h)
    m.addConstr(y[i, "B"] <= x[j, "B"] + x[j, "AB"], f"imp_B_{i}")
    # (1i)
    m.addConstr(y[i, "AB"] <= x[j, "AB"], f"imp_AB_{i}")

# --- Objective (you can later modify for matching preference)
m.setObjective(0, GRB.MAXIMIZE)

# --- Solve
m.optimize()

# --- Print feasible blood types
status = m.Status
if status == GRB.Status.OPTIMAL or status == GRB.Status.SUBOPTIMAL:
    print("Model is feasible.\n")
    for i in pairs:
        print(f"Pair {i}:")
        for t in types:
            if x[i, t].X > 0.5:
                print(f"  Recipient type: {t}")
            if y[i, t].X > 0.5:
                print(f"  Donor type: {t}")
        print()
elif status == GRB.Status.INFEASIBLE:
    print("Model is infeasible.\n")
    m.computeIIS()
    m.write("infeasible_constraints.ilp")
    print("Infeasibility report written to 'infeasible_constraints.ilp'.")
else:
    print(f"⚠️ Solver ended with status code {status}.")
