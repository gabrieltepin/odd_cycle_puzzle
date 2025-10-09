const types = ["O", "A", "B", "AB"];
const pairs = [1, 2, 3];

const compatible = {
  O: ["O", "A", "B", "AB"],
  A: ["A", "AB"],
  B: ["B", "AB"],
  AB: ["AB"]
};

function makeSelect(idPrefix) {
  const sel = document.createElement("select");
  sel.id = idPrefix;
  for (const t of types) {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    sel.appendChild(opt);
  }
  return sel;
}

// Build input interface
const pairsDiv = document.getElementById("pairs");
pairs.forEach((i) => {
  const div = document.createElement("div");
  div.className = "pair";
  div.innerHTML = `<h3>Pair ${i}</h3>`;
  div.append("Donor: ", makeSelect(`donor${i}`), "Recipient: ", makeSelect(`rec${i}`));
  pairsDiv.appendChild(div);
});

// Check feasibility
document.getElementById("check").addEventListener("click", () => {
  let feasible = true;
  let msg = "";

  for (let i of pairs) {
    const donor = document.getElementById(`donor${i}`).value;
    const rec = document.getElementById(`rec${i}`).value;

    // same-pair incompatibility
    if (!compatible[donor].includes(rec)) {
      feasible = false;
      msg += `❌ Pair ${i}: ${donor} → ${rec} is incompatible.<br>`;
    }
  }

  // cyclic compatibility check (1→2→3→1)
  for (let i = 0; i < pairs.length; i++) {
    const donor = document.getElementById(`donor${pairs[i]}`).value;
    const nextRec = document.getElementById(`rec${pairs[(i + 1) % pairs.length]}`).value;
    if (!compatible[donor].includes(nextRec)) {
      feasible = false;
      msg += `⚠️ Donor ${i + 1} cannot donate to next recipient (${nextRec}).<br>`;
    }
  }

  const result = document.getElementById("result");
  if (feasible) {
    result.innerHTML = "✅ Model is feasible.";
    result.style.color = "green";
  } else {
    result.innerHTML = msg + "<br><strong>❌ Model is infeasible.</strong>";
    result.style.color = "red";
  }
});
