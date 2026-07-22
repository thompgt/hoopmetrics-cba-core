// Tab switching
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => { t.classList.remove("active"); t.setAttribute("aria-selected", "false"); });
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    tab.setAttribute("aria-selected", "true");
    document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
  });
});

const money = (n) => {
  const sign = n < 0 ? "-" : "";
  const abs = Math.abs(n);
  return `${sign}$${abs.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
};

const parseNumberList = (raw) =>
  raw.split(",").map((s) => s.trim()).filter((s) => s.length).map(Number);

function animateCount(el, target, isMoney) {
  const duration = 600;
  const start = performance.now();
  const from = 0;
  function tick(now) {
    const progress = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = from + (target - from) * eased;
    el.textContent = isMoney ? money(current) : current.toFixed(2);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function multiplierBar(value, center = 1.0, span = 0.5) {
  const pct = Math.max(0, Math.min(100, ((value - (center - span)) / (span * 2)) * 100));
  return pct;
}

// --- Player Evaluator ---
const playerForm = document.getElementById("player-form");
const playerError = document.getElementById("player-error");
const playerResult = document.getElementById("player-result");

playerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  playerError.classList.remove("show");
  const fd = new FormData(playerForm);
  const payload = {
    name: fd.get("name") || "Player",
    age: Number(fd.get("age")),
    archetype: fd.get("archetype"),
    games_played_last_3: parseNumberList(fd.get("games_played_last_3")),
    box_plus_minus: Number(fd.get("box_plus_minus")),
    on_off: Number(fd.get("on_off")),
    epm: Number(fd.get("epm")),
    cap_hit: Number(fd.get("cap_hit")),
    minutes_per_game: Number(fd.get("minutes_per_game")),
  };

  const btn = playerForm.querySelector("button");
  btn.disabled = true;
  try {
    const res = await fetch("/api/player/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) {
      playerError.textContent = data.error;
      playerError.classList.add("show");
      return;
    }
    renderPlayerResult(data);
  } catch (err) {
    playerError.textContent = "Something went wrong reaching the engine.";
    playerError.classList.add("show");
  } finally {
    btn.disabled = false;
  }
});

function renderPlayerResult(data) {
  const positive = data.final_value >= 0;
  const surplusPositive = data.surplus_value >= 0;

  playerResult.innerHTML = `
    <div class="headline-label">Modeled Value &mdash; ${data.name}</div>
    <div class="headline-value ${positive ? "positive" : "negative"}" id="final-value-el"></div>

    <div class="stat-pair">
      <div class="stat-box">
        <div class="stat-label">Cap Hit</div>
        <div class="stat-value">${money(data.cap_hit)}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Surplus Value</div>
        <div class="stat-value" style="color:${surplusPositive ? "var(--good)" : "var(--bad)"}">${money(data.surplus_value)}</div>
      </div>
    </div>

    <div class="metric-list">
      ${metricRow("Simulated RAPM", data.rapm.toFixed(2))}
      ${metricRow("Parsed EPM", data.epm.toFixed(2))}
      ${metricRow("Net Impact / 100", data.net_impact_per_100.toFixed(2))}
      ${metricRow("Base Value", money(data.base_value))}
      ${metricBar("Age Multiplier", data.age_multiplier)}
      ${metricBar("Injury Discount", data.injury_discount)}
      ${metricBar("Archetype Multiplier", data.archetype_multiplier)}
      ${metricBar("Workload Multiplier", data.workload_multiplier)}
    </div>
  `;
  animateCount(document.getElementById("final-value-el"), data.final_value, true);
}

function metricRow(name, value) {
  return `<div class="metric-row"><span class="metric-name">${name}</span><span class="metric-value">${value}</span></div>`;
}

function metricBar(name, value) {
  const pct = multiplierBar(value);
  return `<div class="metric-row">
    <span class="metric-name">${name}</span>
    <div class="metric-inline">
      <span class="metric-value">${value.toFixed(3)}x</span>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
    </div>
  </div>`;
}

// --- Trade Checker ---
const tradeForm = document.getElementById("trade-form");
const tradeError = document.getElementById("trade-error");
const tradeResult = document.getElementById("trade-result");

tradeForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  tradeError.classList.remove("show");
  const fd = new FormData(tradeForm);
  const toPlayers = (raw) => parseNumberList(raw).map((cap_hit, i) => ({ name: `Player ${i + 1}`, cap_hit }));

  const payload = {
    team_a_apron: fd.get("team_a_apron"),
    team_b_apron: fd.get("team_b_apron"),
    team_a_players: toPlayers(fd.get("team_a_salaries")),
    team_b_players: toPlayers(fd.get("team_b_salaries")),
    team_a_cash: Number(fd.get("team_a_cash")) || 0,
    team_b_cash: Number(fd.get("team_b_cash")) || 0,
  };

  const btn = tradeForm.querySelector("button");
  btn.disabled = true;
  try {
    const res = await fetch("/api/trade/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) {
      tradeError.textContent = data.error;
      tradeError.classList.add("show");
      return;
    }
    renderTradeResult(data);
  } catch (err) {
    tradeError.textContent = "Something went wrong reaching the engine.";
    tradeError.classList.add("show");
  } finally {
    btn.disabled = false;
  }
});

function renderTradeResult(data) {
  const banner = data.legal
    ? `<div class="verdict-banner good">&#9989; Trade is legal</div>`
    : `<div class="verdict-banner bad">&#10060; Trade is blocked</div>`;

  const reasons = data.reasons.length
    ? `<ul class="reason-list">${data.reasons.map((r) => `<li>${escapeHtml(r.replace(/^Trade blocked: /, ""))}</li>`).join("")}</ul>`
    : "";

  tradeResult.innerHTML = `
    ${banner}
    ${reasons}
    <div class="metric-list">
      ${metricRow("Team A Outgoing Salary", money(data.team_a_outgoing_salary))}
      ${metricRow("Team A Max Incoming", money(data.team_a_max_incoming))}
      ${metricRow("Team B Outgoing Salary", money(data.team_b_outgoing_salary))}
      ${metricRow("Team B Max Incoming", money(data.team_b_max_incoming))}
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
