const state = { current: null };
const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusLabel(value) {
  return { ready: "Ready", review: "Review", confirmed: "Confirmed", blocked: "Blocked" }[value] || value;
}

function stateClass(status) {
  if (status === "confirmed" || status === "proposed") return "safe";
  if (status === "refused") return "danger";
  if (status === "needs_clarification") return "warn";
  return "neutral";
}

function render(data) {
  state.current = data;
  const { event, policy, availability, recommendation } = data;
  $("#eventActor").textContent = event.actor;
  $("#eventEta").textContent = event.eta;
  $("#eventInstruction").textContent = event.instruction;
  $("#eventSource").textContent = event.source;
  $("#eventStatus").textContent = event.status;
  $("#dropoffLocation").textContent = policy.safe_dropoff_location;
  $("#residentStatus").textContent = availability.resident_status;
  $("#trustedContacts").textContent = policy.trusted_contacts.join(", ");
  $(".status-summary").dataset.status = data.status;
  $("#statusLabel").textContent = statusLabel(data.status);
  $("#statusDetail").textContent = recommendation ? recommendation.title : "Waiting for a request";

  const decisionStatus = $("#decisionStatus");
  decisionStatus.textContent = recommendation ? statusLabel(recommendation.status) : "Pending";
  decisionStatus.className = `state-pill ${recommendation ? stateClass(recommendation.status) : "neutral"}`;
  renderDecision(recommendation);
  renderMessages(data.messages);
  renderTrace(data.tool_calls);
  renderAudit(data.audit_log);
}

function renderMessages(messages) {
  const list = $("#messageList");
  if (!messages.length) {
    list.innerHTML = '<p class="empty-state">No request yet.</p>';
    return;
  }
  list.innerHTML = messages.map((message) => `
    <div class="message ${message.role}">
      <span class="message-meta">${message.role === "user" ? "You" : "HomeHandoff"}</span>
      ${escapeHtml(message.content)}
    </div>
  `).join("");
  list.scrollTop = list.scrollHeight;
}

function renderDecision(recommendation) {
  const container = $("#decisionContent");
  if (!recommendation) {
    container.innerHTML = '<p class="empty-state">No recommendation yet.</p>';
    return;
  }
  const wrapperClass = recommendation.status === "refused" ? "refusal-box" : recommendation.status === "needs_clarification" ? "clarification-box" : "";
  const button = recommendation.allowed && recommendation.requires_confirmation && recommendation.status === "proposed"
    ? `<button class="confirm-button" data-action-id="${escapeHtml(recommendation.action_id)}" type="button">Confirm simulated notification</button>`
    : "";
  container.innerHTML = `
    <div class="${wrapperClass}">
      <p class="decision-title">${escapeHtml(recommendation.title)}</p>
      <p class="decision-description">${escapeHtml(recommendation.description)}</p>
      <p class="decision-reason"><strong>Why:</strong> ${escapeHtml(recommendation.reason)}</p>
      ${button}
    </div>
  `;
}

function renderTrace(toolCalls) {
  $("#traceCount").textContent = `${toolCalls.length} call${toolCalls.length === 1 ? "" : "s"}`;
  const list = $("#traceList");
  if (!toolCalls.length) {
    list.innerHTML = '<li class="empty-state">No tools called yet.</li>';
    return;
  }
  list.innerHTML = toolCalls.map((call) => {
    const blocked = call.status === "blocked";
    const output = Object.entries(call.output).slice(0, 2).map(([key, value]) => `${key}: ${value}`).join(" · ");
    return `
      <li class="trace-item ${blocked ? "blocked" : ""}">
        <div class="trace-item-head">
          <span class="trace-item-name">${escapeHtml(call.name)}</span>
          <span class="trace-item-status">${blocked ? "blocked" : "completed"}</span>
        </div>
        <p class="trace-item-output">${escapeHtml(output)}</p>
      </li>
    `;
  }).join("");
}

function renderAudit(entries) {
  const list = $("#auditList");
  if (!entries.length) {
    list.innerHTML = '<p class="empty-state">No decisions confirmed.</p>';
    return;
  }
  list.innerHTML = entries.slice().reverse().map((entry) => `
    <div class="audit-entry">
      <strong>${escapeHtml(entry.decision)}</strong>
      <p>${escapeHtml(entry.data_boundary)}</p>
    </div>
  `).join("");
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "The request could not be completed.");
  return payload;
}

async function submitRequest(message) {
  const button = $("#sendButton");
  button.disabled = true;
  button.textContent = "Checking...";
  try {
    render(await requestJson("/api/ask", { method: "POST", body: JSON.stringify({ message }) }));
    $("#requestInput").value = "";
  } catch (error) {
    window.alert(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Send request";
  }
}

$("#requestForm").addEventListener("submit", (event) => {
  event.preventDefault();
  submitRequest($("#requestInput").value.trim());
});

document.addEventListener("click", async (event) => {
  const example = event.target.closest(".example-button");
  if (example) {
    $("#requestInput").value = example.dataset.prompt;
    $("#requestInput").focus();
    return;
  }
  const confirm = event.target.closest(".confirm-button");
  if (!confirm) return;
  confirm.disabled = true;
  confirm.textContent = "Recording...";
  try {
    render(await requestJson("/api/confirm", { method: "POST", body: JSON.stringify({ action_id: confirm.dataset.actionId }) }));
  } catch (error) {
    window.alert(error.message);
    confirm.disabled = false;
    confirm.textContent = "Confirm simulated notification";
  }
});

$("#resetButton").addEventListener("click", async () => {
  render(await requestJson("/api/reset", { method: "POST" }));
});

requestJson("/api/state").then(render).catch((error) => window.alert(error.message));
