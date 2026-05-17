from fastapi import APIRouter
from fastapi.responses import HTMLResponse


def create_ui_router() -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def dashboard():
        return HTMLResponse(DASHBOARD_HTML)

    return router


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Faster Whisper Server</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fa;
      --surface: #ffffff;
      --surface-muted: #f1f4f8;
      --border: #d8dee8;
      --text: #1d2430;
      --muted: #5f6b7a;
      --accent: #156f5b;
      --accent-strong: #0d5c4a;
      --danger: #b42318;
      --shadow: 0 16px 40px rgba(31, 41, 55, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }

    header {
      border-bottom: 1px solid var(--border);
      background: var(--surface);
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      max-width: 1180px;
      min-height: 72px;
      margin: 0 auto;
      padding: 0 28px;
    }

    h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .status {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      white-space: nowrap;
    }

    .dot {
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--accent);
    }

    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px;
    }

    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
      gap: 20px;
      align-items: start;
    }

    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
      background: var(--surface-muted);
    }

    h2 {
      margin: 0;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .panel-body {
      padding: 18px;
    }

    .upload-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
    }

    input[type="file"] {
      width: 100%;
      min-height: 42px;
      padding: 8px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--surface);
      color: var(--text);
    }

    button {
      min-height: 42px;
      padding: 0 16px;
      border: 1px solid transparent;
      border-radius: 6px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover {
      background: var(--accent-strong);
    }

    button.secondary {
      background: var(--surface);
      color: var(--text);
      border-color: var(--border);
    }

    button.secondary:hover {
      background: var(--surface-muted);
    }

    button:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }

    .result {
      min-height: 220px;
      margin-top: 18px;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fbfcfe;
      white-space: pre-wrap;
      line-height: 1.55;
    }

    .metadata {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 14px;
    }

    .metric {
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--surface);
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }

    .metric strong {
      font-size: 18px;
    }

    .stack {
      display: grid;
      gap: 20px;
    }

    dl {
      display: grid;
      grid-template-columns: 120px minmax(0, 1fr);
      gap: 12px;
      margin: 0;
    }

    dt {
      color: var(--muted);
    }

    dd {
      margin: 0;
      overflow-wrap: anywhere;
      font-weight: 600;
    }

    .error {
      color: var(--danger);
      font-weight: 700;
    }

    @media (max-width: 860px) {
      .grid,
      .upload-row,
      .metadata {
        grid-template-columns: 1fr;
      }

      .topbar {
        align-items: flex-start;
        flex-direction: column;
        padding: 18px;
      }

      main {
        padding: 18px;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <h1>Faster Whisper Server</h1>
      <div class="status"><span class="dot"></span><span id="status">Starting</span></div>
    </div>
  </header>

  <main>
    <section class="grid">
      <div class="panel">
        <div class="panel-header">
          <h2>Transcription</h2>
          <button class="secondary" id="refresh" type="button">Refresh</button>
        </div>
        <div class="panel-body">
          <form id="form" class="upload-row">
            <input id="file" type="file" name="file" accept="audio/*,video/*">
            <button id="submit" type="submit">Transcribe</button>
          </form>
          <div id="result" class="result"></div>
          <div class="metadata">
            <div class="metric"><span>Language</span><strong id="language">-</strong></div>
            <div class="metric"><span>Duration</span><strong id="duration">-</strong></div>
            <div class="metric"><span>Queue</span><strong id="queue">-</strong></div>
          </div>
        </div>
      </div>

      <aside class="stack">
        <div class="panel">
          <div class="panel-header"><h2>Model</h2></div>
          <div class="panel-body">
            <dl>
              <dt>Model</dt><dd id="model">-</dd>
              <dt>Device</dt><dd id="device">-</dd>
              <dt>Compute</dt><dd id="compute">-</dd>
              <dt>Batch size</dt><dd id="batch">-</dd>
              <dt>Wait</dt><dd id="wait">-</dd>
            </dl>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header"><h2>Runtime</h2></div>
          <div class="panel-body">
            <dl>
              <dt>Requests</dt><dd id="requests">-</dd>
              <dt>Errors</dt><dd id="errors">-</dd>
              <dt>Rejected</dt><dd id="rejected">-</dd>
              <dt>Timeouts</dt><dd id="timeouts">-</dd>
            </dl>
          </div>
        </div>
      </aside>
    </section>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);

    function parseMetrics(text) {
      const metrics = {};
      for (const line of text.split("\\n")) {
        if (!line || line.startsWith("#")) continue;
        const [name, value] = line.split(" ");
        metrics[name] = Number(value);
      }
      return metrics;
    }

    async function refresh() {
      const [health, model, metricsText] = await Promise.all([
        fetch("/health").then((response) => response.json()),
        fetch("/model").then((response) => response.json()),
        fetch("/metrics").then((response) => response.text()),
      ]);
      const metrics = parseMetrics(metricsText);

      $("status").textContent = health.status;
      $("queue").textContent = health.queue_size;
      $("model").textContent = model.model;
      $("device").textContent = model.device;
      $("compute").textContent = model.compute_type;
      $("batch").textContent = model.max_batch_size;
      $("wait").textContent = `${model.max_wait_ms} ms`;
      $("requests").textContent = metrics.requests_total ?? 0;
      $("errors").textContent = metrics.errors_total ?? 0;
      $("rejected").textContent = metrics.rejected_requests_total ?? 0;
      $("timeouts").textContent = metrics.timeouts_total ?? 0;
    }

    $("refresh").addEventListener("click", refresh);
    $("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const file = $("file").files[0];
      if (!file) return;

      const form = new FormData();
      form.append("file", file);
      $("submit").disabled = true;
      $("result").textContent = "";
      $("language").textContent = "-";
      $("duration").textContent = "-";

      try {
        const response = await fetch("/transcribe", {
          method: "POST",
          body: form,
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || "Transcription failed");
        }

        $("result").textContent = payload.text || "";
        $("language").textContent = payload.language || "-";
        $("duration").textContent = payload.duration
          ? `${payload.duration.toFixed(2)} s`
          : "-";
      } catch (error) {
        $("result").innerHTML = `<span class="error">${error.message}</span>`;
      } finally {
        $("submit").disabled = false;
        refresh();
      }
    });

    refresh();
  </script>
</body>
</html>
"""
