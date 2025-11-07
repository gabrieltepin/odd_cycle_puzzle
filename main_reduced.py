import gurobipy as gp
from gurobipy import GRB
# The reduced formulation model
# --------------------------------------------------------
# Sets
# --------------------------------------------------------
pairs = range(1, 4)  # three donor–recipient pairs (odd cycle)
NUM_PAIRS = len(pairs)
types = ["A", "B"]  # reduced two-type system

# --------------------------------------------------------
# Model
# --------------------------------------------------------
m = gp.Model("reduced_abo_only_kep")

# Decision variables
x = m.addVars(pairs, types, vtype=GRB.BINARY, name="x")  # recipient blood type
y = m.addVars(pairs, types, vtype=GRB.BINARY, name="y")  # donor blood type

# --------------------------------------------------------
# (1) Assignment constraints
# eqs (redassign1)–(redassign2)
# --------------------------------------------------------
for i in pairs:
    m.addConstr(x[i, "A"] + x[i, "B"] == 1, f"assign_x_{i}")
    m.addConstr(y[i, "A"] + y[i, "B"] == 1, f"assign_y_{i}")

# --------------------------------------------------------
# (2) Internal incompatibility
# eqs (redconflict2)–(redconflict7)
# --------------------------------------------------------
for i in pairs:
    # donor A incompatible with recipient A
    m.addConstr(y[i, "A"] <= 1 - x[i, "A"], f"incomp1_{i}")
    # donor B incompatible with recipient B
    m.addConstr(y[i, "B"] <= 1 - x[i, "B"], f"incomp2_{i}")
    # symmetric (redundant but pedagogically explicit)
    m.addConstr(x[i, "A"] <= 1 - y[i, "A"], f"incomp3_{i}")
    m.addConstr(x[i, "B"] <= 1 - y[i, "B"], f"incomp4_{i}")

# --------------------------------------------------------
# (3) Cycle implications
# eqs (redimplied2)–(redimplied7)
# --------------------------------------------------------
for i in pairs:
    j = 1 + (i % NUM_PAIRS)  # cyclic next pair
    # donor A in pair i can only donate to recipient A in pair j
    m.addConstr(y[i, "A"] <= x[j, "A"], f"imp1_{i}")
    # donor B in pair i can only donate to recipient B in pair j
    m.addConstr(y[i, "B"] <= x[j, "B"], f"imp2_{i}")
    # symmetric reverse implications (redundant but shown in full)
    m.addConstr(x[j, "A"] <= y[i, "A"], f"imp3_{i}")
    m.addConstr(x[j, "B"] <= y[i, "B"], f"imp4_{i}")

# --------------------------------------------------------
# (4) Binary domain (already binary)
# --------------------------------------------------------

# No objective — pure feasibility
m.setObjective(0, GRB.MAXIMIZE)
m.optimize()

# --------------------------------------------------------
# Results
# --------------------------------------------------------
status = m.Status
if status in (GRB.Status.OPTIMAL, GRB.Status.SUBOPTIMAL):
    print("\n✅ Model is feasible (reduced formulation).\n")
    for i in pairs:
        rec_type = [t for t in types if x[i, t].X > 0.5][0]
        don_type = [t for t in types if y[i, t].X > 0.5][0]
        print(f"Pair {i}: Recipient {rec_type} ← Donor {don_type}")
elif status == GRB.Status.INFEASIBLE:
    print("\n❌ Model is infeasible (no odd-length ABO-only cycle exists).\n")
    m.computeIIS()
    m.write("infeasible_reduced.ilp")
else:
    print(f"\n⚠️ Solver ende