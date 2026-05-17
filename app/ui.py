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
      --page: #f4f6f8;
      --nav: #18202a;
      --nav-muted: #9aa7b5;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --border: #d9e0e8;
      --border-strong: #c3ccd6;
      --text: #17202a;
      --muted: #657283;
      --accent: #087f5b;
      --accent-soft: #e8f5ef;
      --danger: #b42318;
      --warning: #ad5f00;
      --shadow: 0 18px 45px rgba(24, 32, 42, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--page);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }

    .shell {
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      background: var(--nav);
      color: #ffffff;
      padding: 24px 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-height: 44px;
      margin-bottom: 32px;
    }

    .brand-mark {
      display: grid;
      place-items: center;
      width: 40px;
      height: 40px;
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.08);
      font-weight: 800;
    }

    .brand h1 {
      margin: 0;
      font-size: 15px;
      line-height: 1.25;
      letter-spacing: 0;
    }

    .brand span {
      display: block;
      margin-top: 2px;
      color: var(--nav-muted);
      font-size: 12px;
      font-weight: 500;
    }

    .nav-section {
      margin-top: 24px;
    }

    .nav-label {
      margin: 0 0 10px;
      color: var(--nav-muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 38px;
      padding: 0 10px;
      border-radius: 6px;
      color: #dce4ec;
    }

    .nav-item.active {
      background: rgba(255, 255, 255, 0.1);
      color: #ffffff;
    }

    .nav-icon {
      width: 16px;
      height: 16px;
      border: 1.7px solid currentColor;
      border-radius: 4px;
    }

    .main {
      min-width: 0;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      min-height: 72px;
      padding: 0 30px;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
    }

    .title h2 {
      margin: 0;
      font-size: 20px;
      letter-spacing: 0;
    }

    .title p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid #b7dfcf;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 700;
      white-space: nowrap;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--accent);
    }

    .content {
      padding: 28px 30px 34px;
    }

    .summary {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }

    .tile {
      min-height: 96px;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: var(--shadow);
    }

    .tile span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .tile strong {
      display: block;
      margin-top: 12px;
      font-size: 26px;
      line-height: 1;
      letter-spacing: 0;
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 18px;
      align-items: start;
    }

    .panel {
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      min-height: 58px;
      padding: 0 18px;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
    }

    .panel-header h3 {
      margin: 0;
      font-size: 14px;
      letter-spacing: 0;
    }

    .panel-body {
      padding: 18px;
    }

    .upload-zone {
      position: relative;
      display: grid;
      place-items: center;
      min-height: 178px;
      padding: 24px;
      border: 1.5px dashed var(--border-strong);
      border-radius: 8px;
      background: var(--surface-soft);
      text-align: center;
      transition: border-color 0.15s ease, background 0.15s ease;
    }

    .upload-zone.active,
    .upload-zone:hover {
      border-color: var(--accent);
      background: #f1fbf7;
    }

    .upload-zone input {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
    }

    .upload-mark {
      display: grid;
      place-items: center;
      width: 44px;
      height: 44px;
      margin: 0 auto 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      color: var(--accent);
      font-weight: 900;
      font-size: 24px;
    }

    .upload-title {
      margin: 0;
      font-size: 15px;
      font-weight: 800;
    }

    .upload-meta {
      margin: 7px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 14px;
    }

    .file-name {
      min-width: 0;
      color: var(--muted);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    button {
      min-height: 40px;
      padding: 0 15px;
      border: 1px solid transparent;
      border-radius: 6px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 800;
      cursor: pointer;
    }

    button:hover {
      background: #066b4d;
    }

    button:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }

    .secondary {
      background: var(--surface);
      color: var(--text);
      border-color: var(--border-strong);
    }

    .secondary:hover {
      background: var(--surface-soft);
    }

    .result {
      min-height: 250px;
      margin-top: 18px;
      padding: 18px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fbfcfe;
      color: var(--text);
      white-space: pre-wrap;
      line-height: 1.6;
    }

    .result.empty {
      display: grid;
      place-items: center;
      color: var(--muted);
      text-align: center;
    }

    .details {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }

    .detail {
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
    }

    .detail span,
    dt {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .detail strong {
      display: block;
      margin-top: 8px;
      font-size: 18px;
      overflow-wrap: anywhere;
    }

    .side-stack {
      display: grid;
      gap: 18px;
    }

    dl {
      display: grid;
      grid-template-columns: 112px minmax(0, 1fr);
      gap: 13px 12px;
      margin: 0;
    }

    dd {
      margin: 0;
      min-width: 0;
      overflow-wrap: anywhere;
      font-weight: 700;
    }

    .error {
      color: var(--danger);
      font-weight: 800;
    }

    @media (max-width: 980px) {
      .shell {
        grid-template-columns: 1fr;
      }

      .sidebar {
        display: none;
      }

      .workspace {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 720px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
        padding: 18px;
      }

      .content {
        padding: 18px;
      }

      .summary,
      .details {
        grid-template-columns: 1fr;
      }

      .actions {
        align-items: stretch;
        flex-direction: column;
      }

      .file-name {
        white-space: normal;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">W</div>
        <div>
          <h1>Whisper Server</h1>
          <span>Inference dashboard</span>
        </div>
      </div>

      <div class="nav-section">
        <p class="nav-label">Workspace</p>
        <div class="nav-item active"><span class="nav-icon"></span>Transcription</div>
        <div class="nav-item"><span class="nav-icon"></span>Scheduler</div>
        <div class="nav-item"><span class="nav-icon"></span>Monitoring</div>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="title">
          <h2>Faster Whisper Server</h2>
          <p id="subtitle">Model and scheduler status are loading</p>
        </div>
        <div class="status-pill"><span class="status-dot"></span><span id="status">Starting</span></div>
      </header>

      <main class="content">
        <section class="summary">
          <div class="tile"><span>Queue</span><strong id="queue">-</strong></div>
          <div class="tile"><span>Requests</span><strong id="requests">-</strong></div>
          <div class="tile"><span>Errors</span><strong id="errors">-</strong></div>
          <div class="tile"><span>Rejected</span><strong id="rejected">-</strong></div>
        </section>

        <section class="workspace">
          <div class="panel">
            <div class="panel-header">
              <h3>Transcription</h3>
              <button class="secondary" id="refresh" type="button">Refresh</button>
            </div>
            <div class="panel-body">
              <form id="form">
                <label class="upload-zone" id="dropzone">
                  <input id="file" type="file" name="file" accept="audio/*,video/*">
                  <div>
                    <div class="upload-mark">+</div>
                    <p class="upload-title">Choose an audio file</p>
                    <p class="upload-meta">WAV, MP3, MP4, M4A, WEBM and other ffmpeg-supported files</p>
                  </div>
                </label>
                <div class="actions">
                  <div class="file-name" id="fileName">No file selected</div>
                  <button id="submit" type="submit">Transcribe</button>
                </div>
              </form>

              <div id="result" class="result empty">Transcription output will appear here.</div>

              <div class="details">
                <div class="detail"><span>Language</span><strong id="language">-</strong></div>
                <div class="detail"><span>Duration</span><strong id="duration">-</strong></div>
                <div class="detail"><span>Timeouts</span><strong id="timeouts">-</strong></div>
              </div>
            </div>
          </div>

          <aside class="side-stack">
            <div class="panel">
              <div class="panel-header"><h3>Model</h3></div>
              <div class="panel-body">
                <dl>
                  <dt>Model</dt><dd id="model">-</dd>
                  <dt>Device</dt><dd id="device">-</dd>
                  <dt>Compute</dt><dd id="compute">-</dd>
                  <dt>Pipeline</dt><dd id="pipeline">-</dd>
                </dl>
              </div>
            </div>

            <div class="panel">
              <div class="panel-header"><h3>Scheduler</h3></div>
              <div class="panel-body">
                <dl>
                  <dt>Batch size</dt><dd id="batch">-</dd>
                  <dt>Wait</dt><dd id="wait">-</dd>
                  <dt>Queue limit</dt><dd id="queueLimit">-</dd>
                  <dt>Timeout</dt><dd id="timeout">-</dd>
                </dl>
              </div>
            </div>
          </aside>
        </section>
      </main>
    </div>
  </div>

  <script>
    const $ = (id) => document.getElementById(id);
    const fileInput = $("file");
    const dropzone = $("dropzone");
    const submit = $("submit");
    const result = $("result");

    function parseMetrics(text) {
      const metrics = {};
      for (const line of text.split("\\n")) {
        if (!line || line.startsWith("#")) continue;
        const [name, value] = line.split(" ");
        metrics[name] = Number(value);
      }
      return metrics;
    }

    function setResult(text, isError = false) {
      result.classList.toggle("empty", !text);
      result.innerHTML = isError
        ? `<span class="error">${text}</span>`
        : text || "Transcription output will appear here.";
    }

    async function refresh() {
      const [health, model, metricsText] = await Promise.all([
        fetch("/health").then((response) => response.json()),
        fetch("/model").then((response) => response.json()),
        fetch("/metrics").then((response) => response.text()),
      ]);
      const metrics = parseMetrics(metricsText);

      $("status").textContent = health.status;
      $("subtitle").textContent = `${model.model} on ${model.device}`;
      $("queue").textContent = health.queue_size;
      $("requests").textContent = metrics.requests_total ?? 0;
      $("errors").textContent = metrics.errors_total ?? 0;
      $("rejected").textContent = metrics.rejected_requests_total ?? 0;
      $("timeouts").textContent = metrics.timeouts_total ?? 0;
      $("model").textContent = model.model;
      $("device").textContent = model.device;
      $("compute").textContent = model.compute_type;
      $("pipeline").textContent = model.batched_pipeline ? "Batched" : "Standard";
      $("batch").textContent = model.max_batch_size;
      $("wait").textContent = `${model.max_wait_ms} ms`;
      $("queueLimit").textContent = model.queue_max_size;
      $("timeout").textContent = `${model.request_timeout_seconds} s`;
    }

    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      $("fileName").textContent = file ? file.name : "No file selected";
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, () => dropzone.classList.add("active"));
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropzone.addEventListener(eventName, () => dropzone.classList.remove("active"));
    });

    $("refresh").addEventListener("click", refresh);
    $("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const file = fileInput.files[0];
      if (!file) return;

      const form = new FormData();
      form.append("file", file);
      submit.disabled = true;
      submit.textContent = "Running";
      setResult("");
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

        result.classList.remove("empty");
        setResult(payload.text || "");
        $("language").textContent = payload.language || "-";
        $("duration").textContent = payload.duration
          ? `${payload.duration.toFixed(2)} s`
          : "-";
      } catch (error) {
        setResult(error.message, true);
      } finally {
        submit.disabled = false;
        submit.textContent = "Transcribe";
        refresh();
      }
    });

    refresh();
  </script>
</body>
</html>
"""
