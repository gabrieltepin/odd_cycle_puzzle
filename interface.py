import streamlit as st
import gurobipy as gp
from gurobipy import GRB

st.set_page_config(page_title="Blood-Type Incompatibility Model", page_icon="🩸")

st.title("🩸 Blood-Type Incompatibility Model")
st.markdown("""
This interactive demo uses **Gurobi** to test whether a simplified blood-type
exchange model is **feasible or infeasible** under ABO rules.

Click **Run Optimization** to check if a feasible combination of donor and
recipient types exists under the given logical constraints.
""")

pairs = [1, 2, 3]
types = ["O", "A", "B", "AB"]

if st.button("Run Optimization"):
    m = gp.Model("blood_incompatibility")
    m.Params.OutputFlag = 0

    # Variables
    x = m.addVars(pairs, types, vtype=GRB.BINARY, name="x")
    y = m.addVars(pairs, types, vtype=GRB.BINARY, name="y")

    # Each donor/recipient has exactly one type
    for i in pairs:
        m.addConstr(gp.quicksum(x[i, t] for t in types) == 1, f"one_type_rec_{i}")
        m.addConstr(gp.quicksum(y[i, t] for t in types) == 1, f"one_type_don_{i}")

    # Incompatibility within same pair
    for i in pairs:
        m.addConstr(y[i, "O"]  <= 1 - (x[i, "O"] + x[i, "A"]+ x[i, "B"]+ x[i, "AB"]), f"incomp_O_{i}")
        m.addConstr(y[i, "A"]  <= 1 - (x[i, "A"] + x[i, "AB"]), f"incomp_A_{i}")
        m.addConstr(y[i, "B"]  <= 1 - (x[i, "B"] + x[i, "AB"]), f"incomp_B_{i}")
        m.addConstr(y[i, "AB"] <= 1 - (x[i, "AB"]), f"incomp_AB_{i}")

    # Implication across consecutive pairs
    for i in pairs:
        j = 1 + (i % 3)  # 1→2, 2→3, 3→1
        m.addConstr(y[i, "A"]  <= x[j, "A"] + x[j, "AB"], f"imp_A_{i}")
        m.addConstr(y[i, "B"]  <= x[j, "B"] + x[j, "AB"], f"imp_B_{i}")
        m.addConstr(y[i, "AB"] <= x[j, "AB"], f"imp_AB_{i}")

    m.setObjective(0, GRB.MAXIMIZE)
    m.optimize()

    status = m.Status

    # Show result
    if status in [GRB.Status.OPTIMAL, GRB.Status.SUBOPTIMAL]:
        st.success("✅ Model is feasible.")
        for i in pairs:
            st.subheader(f"Pair {i}")
            rec_type = next(t for t in types if x[i, t].X > 0.5)
            don_type = next(t for t in types if y[i, t].X > 0.5)
            st.write(f"Recipient type: **{rec_type}**")
            st.write(f"Donor type: **{don_type}**")
    elif status == GRB.Status.INFEASIBLE:
        st.error("❌ Model is infeasible.")
        m.computeIIS()
        m.write("infeasible_constraints.ilp")
        with open("infeasible_constraints.ilp") as f:
            st.download_button(
                label="📥 Download infeasibility report",
                data=f.read(),
                file_name="infeasible_constraints.ilp"
            )
    else:
        st.warning(f"Solver ended with status code {status}.")
