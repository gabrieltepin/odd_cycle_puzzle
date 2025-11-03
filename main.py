import gurobipy as gp
from gurobipy import GRB

# --------------------------------------------------------
# Sets
# --------------------------------------------------------
pairs = range(1,4)  # three donor–recipient pairs in cyclic order
NUM_PAIRS = len(pairs)
types = ["O", "A", "B", "AB"]

# ABO compatibility: donor_type -> compatible recipient types
compat = {
    "O": ["O", "A", "B", "AB"],
    "A": ["A", "AB"],
    "B": ["B", "AB"],
    "AB": ["AB"]
}

# --------------------------------------------------------
# Model
# --------------------------------------------------------
m = gp.Model("abo_only_kep")

# Decision variables
x = m.addVars(pairs, types, vtype=GRB.BINARY, name="x")  # recipient blood type
y = m.addVars(pairs, types, vtype=GRB.BINARY, name="y")  # donor blood type

# --------------------------------------------------------
# (1) Assignment constraints — one type per person
# eqs (assign1)–(assign2)
# --------------------------------------------------------
for i in pairs:
    m.addConstr(gp.quicksum(x[i, t] for t in types) == 1, f"one_type_rec_{i}")
    m.addConstr(gp.quicksum(y[i, t] for t in types) == 1, f"one_type_don_{i}")

# --------------------------------------------------------
# (2) Internal incompatibility — donor and recipient in same pair cannot match
# eqs (conflict1)–(conflict8)
# --------------------------------------------------------
for i in pairs:
    for dt in types:
        for rt in types:
            if rt in compat[dt]:  # if compatible → forbid both being 1
                m.addConstr(y[i, dt] + x[i, rt] <= 1, f"incomp_{i}_{dt}_{rt}")

# --------------------------------------------------------
# (3) Cycle implications — donor of pair i must be compatible with recipient of pair j
# eqs (implied1)–(implied8)
# --------------------------------------------------------
for i in pairs:
    j = 1 + (i % NUM_PAIRS)  # cyclic next pair: 1→2, 2→3, 3→1
    for dt in types:
        for rt in types:
            if rt not in compat[dt]:
                m.addConstr(y[i, dt] + x[j, rt] <= 1, f"imp_{i}_{j}_{dt}_{rt}")

# --------------------------------------------------------
# (4) Variable fixings (derived algebraically)
# --------------------------------------------------------

# (a) Fix y[d_i, O] = 0  ---- paragraph: "Fixing y_{d_i,O} to zero"
for i in pairs:
    m.addConstr(y[i, "O"] == 0, f"fix_y_O_{i}")

# (b) Fix x[r_i, AB] = 0  ---- paragraph: "Fixing x_{r_i,AB} to zero"
for i in pairs:
    m.addConstr(x[i, "AB"] == 0, f"fix_x_AB_{i}")

# (c) Fix y[d_i, AB] = 0  ---- paragraph: "Fixing y_{d_i,AB} to zero"
for i in pairs:
    m.addConstr(y[i, "AB"] == 0, f"fix_y_AB_{i}")

# (d) Fix x[r_i, O] = 0  ---- paragraph: "Fixing x_{r_j,O} to zero"
for i in pairs:
    m.addConstr(x[i, "O"] == 0, f"fix_x_O_{i}")

# --------------------------------------------------------
# (5) Binary domain (already binary)
# --------------------------------------------------------

# No objective — pure feasibility
m.setObjective(0, GRB.MAXIMIZE)
m.optimize()

# --------------------------------------------------------
# Results
# --------------------------------------------------------
status = m.Status
if status in (GRB.Status.OPTIMAL, GRB.Status.SUBOPTIMAL):
    print("\n✅ Model is feasible.\n")
    for i in pairs:
        rec_type = [t for t in types if x[i, t].X > 0.5][0]
        don_type = [t for t in types if y[i, t].X > 0.5][0]
        print(f"Pair {i}: Recipient {rec_type} ← Donor {don_type}")
elif status == GRB.Status.INFEASIBLE:
    print("\n❌ Model is infeasible (no odd-length ABO-only cycle exists).\n")
    m.computeIIS()
    m.write("infeasible_constraints.ilp")
else:
    print(f"\n⚠️ Solver ended with status code {status}.")
