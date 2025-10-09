const types = ["O", "A", "B", "AB"];
const compatible = {
  O: ["O", "A", "B", "AB"],
  A: ["A", "AB"],
  B: ["B", "AB"],
  AB: ["AB"]
};

// initialize dropdowns
for (let i = 1; i <= 3; i++) {
  const rec = document.getElementById(`rec${i}`);
  const don = document.getElementById(`don${i}`);
  for (const t of types) {
    rec.innerHTML += `<option value="${t}">${t}</option>`;
    don.innerHTML += `<option value="${t}">${t}</option>`;
  }
}

document.getElementById("check").addEventListener("click", () => {
  let feasible = true;
  let messages = [];

  // reset arrow colors
  for (let l = 1; l <= 3; l++) {
    document.getElementById(`line${l}`).style.stroke = "#888";
  }

  // Check internal incompatibilities
  for (let i = 1; i <= 3; i++) {
    const donor = document.getElementById(`don${i}`).value;
    const rec = document.getElementById(`rec${i}`).value;
    if (!compatible[donor].includes(rec)) {
      feasible = false;
      messages.push(`❌ Pair ${i}: Donor ${donor} incompatible with Recipient ${rec}`);
    }
  }

  // cyclic connections (1→2, 2→3, 3→1)
  const next = {1:2, 2:3, 3:1};
  for (let i = 1; i <= 3; i++) {
    const donor = document.getElementById(`don${i}`).value;
    const nextRec = document.getElementById(`rec${next[i]}`).value;
    const line = document.getElementById(`line${i}`);
    if (compatible[donor].includes(nextRec)) {
      line.style.stroke = "green";
    } else {
      line.style.stroke = "red";
      feasible = false;
      messages.push(`⚠️ Donor ${i} (${donor}) cannot donate to Recipient ${next[i]} (${nextRec})`);
    }
  }

  const result = document.getElementById("result");
  if (feasible) {
    result.innerHTML = "✅ Model is feasible.";
    result.style.color = "green";
  } else {
    result.innerHTML = messages.join("<br>") + "<br><strong>❌ Model is infeasible.</strong>";
    result.style.color = "red";
  }
});
