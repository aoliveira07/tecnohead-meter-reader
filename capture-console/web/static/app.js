const $ = (selector) => document.querySelector(selector);
const formatBytes = (value) => {
  if (!Number.isFinite(value)) return "—";
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KiB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MiB`;
};
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[char]));

async function json(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `HTTP ${response.status}`);
  return body;
}

function renderFrames(records) {
  const frames = records.filter((record) => record.type === "frame").slice(0, 24);
  if (!frames.length) { $("#frames").innerHTML = '<p class="muted">Nenhum frame recebido.</p>'; return; }
  $("#frames").innerHTML = frames.map((frame) => `
    <article class="frame">
      <div class="frame-meta"><span>seq ${escapeHtml(frame.sequence)}</span><span>${escapeHtml(frame.length)} bytes</span><span>${escapeHtml(frame.received_at)}</span><span>${escapeHtml(frame.baud)} ${escapeHtml(frame.data_bits)}${escapeHtml(frame.parity)}${escapeHtml(frame.stop_bits)}</span></div>
      <div class="frame-hex">${escapeHtml(frame.hex)}</div>
    </article>`).join("");
}

function renderSessions(sessions) {
  if (!sessions.length) { $("#sessions").innerHTML = '<p class="muted">Nenhuma sessão criada.</p>'; return; }
  $("#sessions").innerHTML = sessions.map((session) => `
    <article class="session">
      <div><div class="session-title">${escapeHtml(session.device)} · sessão ${escapeHtml(session.session)}</div>
      <small>${escapeHtml(session.started_at)} · ${escapeHtml(session.frames)} frames · ${formatBytes(session.bytes_written)} · ${session.incomplete ? "INCOMPLETA" : "completa até o último evento"}</small></div>
      <div class="session-actions"><a href="/api/sessions/${encodeURIComponent(session.key)}/bin"><button>.bin</button></a><a href="/api/sessions/${encodeURIComponent(session.key)}/jsonl"><button>.jsonl</button></a><a href="/api/sessions/${encodeURIComponent(session.key)}/csv"><button>.csv</button></a></div>
    </article>`).join("");
}

async function refresh() {
  try {
    const [status, sessions, recent] = await Promise.all([json("/api/status"), json("/api/sessions"), json("/api/recent")]);
    const mqttOnline = Boolean(status.mqtt.connected);
    $("#mqtt-state").textContent = mqttOnline ? "MQTT conectado" : "MQTT offline";
    $("#mqtt-state").className = `badge ${mqttOnline ? "online" : "offline"}`;
    $("#capture-state").textContent = mqttOnline ? "online" : "offline";
    $("#capture-state").className = `status-dot ${mqttOnline ? "online" : "offline"}`;
    $("#message-count").textContent = status.capture.messages;
    $("#dropped-count").textContent = status.capture.dropped_messages;
    $("#last-received").textContent = status.capture.last_received_at || "—";
    $("#storage").textContent = `${formatBytes(status.capture.storage_bytes)} / ${formatBytes(status.capture.max_total_bytes)}`;
    $("#error-state").textContent = status.mqtt.last_error || status.capture.last_error || "Canal pronto; aguardando ou recebendo sessões.";
    renderFrames(recent);
    renderSessions(sessions);
  } catch (error) {
    $("#error-state").textContent = error.message;
  }
}

document.querySelectorAll("button[data-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    button.disabled = true;
    try { await json(`/api/command/${button.dataset.command}`, {method: "POST"}); await refresh(); }
    catch (error) { $("#error-state").textContent = error.message; }
    finally { button.disabled = false; }
  });
});

refresh();
setInterval(refresh, 1500);
