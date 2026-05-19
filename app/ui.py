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
      width: 100%;
      min-height: 38px;
      padding: 0 10px;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: #dce4ec;
      font: inherit;
      font-weight: 700;
      text-align: left;
      cursor: pointer;
    }

    .nav-item:hover,
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

    .top-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
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

    .tile:hover {
      border-color: var(--border);
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

    .metric-note {
      display: block;
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
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

    .panel-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
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
    .upload-zone.has-file,
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

    .file-card {
      display: none;
      grid-template-columns: minmax(0, 1fr);
      gap: 12px;
      margin-top: 14px;
      padding: 14px;
      border: 1px solid #b7dfcf;
      border-radius: 8px;
      background: var(--accent-soft);
    }

    .file-card.visible {
      display: grid;
    }

    .file-list {
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }

    .file-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: start;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
    }

    .file-card strong {
      display: block;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .file-card span {
      display: block;
      margin-top: 5px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .file-result {
      grid-column: 1 / -1;
      display: none;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fbfcfe;
      white-space: pre-wrap;
      line-height: 1.5;
    }

    .file-result.visible {
      display: block;
    }

    .progress {
      grid-column: 1 / -1;
      height: 8px;
      overflow: hidden;
      border-radius: 999px;
      background: #d7eadf;
    }

    .progress div {
      width: 0;
      height: 100%;
      border-radius: inherit;
      background: var(--accent);
      transition: width 0.2s ease;
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

    .ghost {
      min-height: 34px;
      padding: 0 12px;
      background: transparent;
      color: var(--text);
      border-color: var(--border);
    }

    .secondary:hover {
      background: var(--surface-soft);
    }

    .ghost:hover {
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

      .file-card {
        grid-template-columns: 1fr;
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
        <button class="nav-item active" data-target="transcriptionPanel" type="button"><span class="nav-icon"></span>Transcription</button>
        <button class="nav-item" data-target="modelPanel" type="button"><span class="nav-icon"></span>Model</button>
        <button class="nav-item" data-target="schedulerPanel" type="button"><span class="nav-icon"></span>Runtime</button>
      </div>
    </aside>

    <div class="main">
      <header class="topbar">
        <div class="title">
          <h2>Faster Whisper Server</h2>
          <p id="subtitle">Model and scheduler status are loading</p>
        </div>
        <div class="top-actions">
          <button class="secondary" id="openDocs" type="button" title="Open FastAPI Swagger documentation">API Docs</button>
          <button class="secondary" id="openMetrics" type="button" title="Open raw Prometheus metrics">Metrics</button>
          <div class="status-pill" title="Server health status"><span class="status-dot"></span><span id="status">Starting</span></div>
        </div>
      </header>

      <main class="content">
        <section class="summary" id="monitoringPanel">
          <div class="tile"><span>Queue</span><strong id="queue">-</strong><small class="metric-note">Waiting requests right now</small></div>
          <div class="tile"><span>Requests</span><strong id="requests">-</strong><small class="metric-note">Accepted requests total</small></div>
          <div class="tile"><span>Errors</span><strong id="errors">-</strong><small class="metric-note">Failed requests total</small></div>
          <div class="tile"><span>Rejected</span><strong id="rejected">-</strong><small class="metric-note">Queue-full rejections total</small></div>
        </section>

        <section class="workspace">
          <div class="panel" id="transcriptionPanel">
            <div class="panel-header">
              <h3>Transcription</h3>
              <div class="panel-actions">
                <button class="secondary" id="refresh" type="button">Refresh</button>
              </div>
            </div>
            <div class="panel-body">
              <form id="form">
                <label class="upload-zone" id="dropzone">
                  <input id="file" type="file" name="file" accept="audio/*,video/*" multiple>
                  <div>
                    <div class="upload-mark">+</div>
                    <p class="upload-title" id="uploadTitle">Choose audio files</p>
                    <p class="upload-meta" id="uploadMeta">Select or drag multiple WAV, MP3, MP4, M4A, WEBM files</p>
                  </div>
                </label>
                <div class="file-card" id="selectedFile">
                  <div>
                    <strong id="selectedFileName">No files selected</strong>
                    <span id="selectedFileMeta">Waiting for audio files</span>
                  </div>
                  <div class="progress"><div id="uploadProgress"></div></div>
                  <div class="file-list" id="fileList"></div>
                </div>
                <div class="actions">
                  <div class="file-name" id="fileName">No files selected</div>
                  <div class="panel-actions">
                    <button class="ghost" id="clearFile" type="button">Remove all</button>
                    <button id="submit" type="submit" disabled>Transcribe all</button>
                  </div>
                </div>
              </form>

              <div class="panel-header" style="margin: 18px -18px 0; border-top: 1px solid var(--border);">
                <h3>Result</h3>
                <div class="panel-actions">
                  <button class="ghost" id="copyResult" type="button">Copy</button>
                  <button class="ghost" id="clearResult" type="button">Clear</button>
                </div>
              </div>
              <div id="result" class="result empty">Batch transcription output will appear here.</div>

              <div class="details">
                <div class="detail"><span>Language</span><strong id="language">-</strong></div>
                <div class="detail"><span>Duration</span><strong id="duration">-</strong></div>
                <div class="detail"><span>Timeouts</span><strong id="timeouts">-</strong></div>
              </div>
            </div>
          </div>

          <aside class="side-stack">
            <div class="panel" id="modelPanel">
              <div class="panel-header">
                <h3>Model</h3>
                <button class="ghost" id="openModel" type="button">Open</button>
              </div>
              <div class="panel-body">
                <dl>
                  <dt>Model</dt><dd id="model">-</dd>
                  <dt>Source</dt><dd id="modelSource">-</dd>
                  <dt>Device</dt><dd id="device">-</dd>
                  <dt>Compute</dt><dd id="compute">-</dd>
                  <dt>Pipeline</dt><dd id="pipeline">-</dd>
                  <dt>Language</dt><dd id="modelLanguage">-</dd>
                  <dt>Task</dt><dd id="modelTask">-</dd>
                </dl>
              </div>
            </div>

            <div class="panel" id="schedulerPanel">
              <div class="panel-header">
                <h3>Scheduler</h3>
                <button class="ghost" id="refreshScheduler" type="button">Refresh</button>
              </div>
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
    let selectedFiles = [];
    let latestTranscription = "";

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
      latestTranscription = isError ? "" : text;
      result.classList.toggle("empty", !text);
      result.textContent = text || "Batch transcription output will appear here.";
      result.classList.toggle("error", isError);
    }

    function formatBytes(bytes) {
      if (!bytes) return "0 B";
      const units = ["B", "KB", "MB", "GB"];
      const index = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
      );
      return `${(bytes / Math.pow(1024, index)).toFixed(index ? 2 : 0)} ${units[index]}`;
    }

    function setUploadProgress(percent, label) {
      $("uploadProgress").style.width = `${Math.max(0, Math.min(percent, 100))}%`;
      if (label) {
        $("selectedFileMeta").textContent = label;
      }
    }

    function selectFiles(files, append = false) {
      const incomingFiles = Array.from(files || []);
      selectedFiles = append
        ? mergeFiles(selectedFiles, incomingFiles)
        : incomingFiles;
      renderFileList();
      submit.disabled = selectedFiles.length === 0;
      dropzone.classList.toggle("has-file", selectedFiles.length > 0);
      $("selectedFile").classList.toggle("visible", selectedFiles.length > 0);
      $("fileName").textContent = selectedFiles.length
        ? `${selectedFiles.length} file${selectedFiles.length === 1 ? "" : "s"} selected`
        : "No files selected";
      $("selectedFileName").textContent = selectedFiles.length
        ? `${selectedFiles.length} audio file${selectedFiles.length === 1 ? "" : "s"} ready`
        : "No files selected";
      $("selectedFileMeta").textContent = selectedFiles.length
        ? `${formatBytes(totalSelectedBytes())} total selected`
        : "Waiting for audio files";
      $("uploadTitle").textContent = selectedFiles.length
        ? "Audio files selected"
        : "Choose audio files";
      $("uploadMeta").textContent = selectedFiles.length
        ? "Ready to transcribe. Choose more files to add them to this batch."
        : "Select or drag multiple WAV, MP3, MP4, M4A, WEBM files";
      setUploadProgress(selectedFiles.length ? 100 : 0);
    }

    function mergeFiles(existingFiles, incomingFiles) {
      const seen = new Set(
        existingFiles.map((file) => `${file.name}:${file.size}:${file.lastModified}`)
      );
      const merged = [...existingFiles];
      for (const file of incomingFiles) {
        const key = `${file.name}:${file.size}:${file.lastModified}`;
        if (!seen.has(key)) {
          seen.add(key);
          merged.push(file);
        }
      }
      return merged;
    }

    function totalSelectedBytes() {
      return selectedFiles.reduce((total, file) => total + file.size, 0);
    }

    function renderFileList() {
      $("fileList").innerHTML = selectedFiles
        .map((file, index) => `
          <div class="file-row" id="fileRow-${index}">
            <div>
              <strong>${escapeHtml(file.name)}</strong>
              <span id="fileStatus-${index}">${formatBytes(file.size)} ready</span>
            </div>
            <button class="ghost" data-remove-index="${index}" type="button">Remove</button>
            <div class="progress"><div id="fileProgress-${index}"></div></div>
            <div class="file-result" id="fileResult-${index}"></div>
          </div>
        `)
        .join("");

      document.querySelectorAll("[data-remove-index]").forEach((button) => {
        button.addEventListener("click", () => {
          selectedFiles.splice(Number(button.dataset.removeIndex), 1);
          renderFileList();
          selectFiles(selectedFiles);
        });
      });
    }

    function escapeHtml(value) {
      return value.replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[char]));
    }

    function transcribeWithProgress(file, index) {
      return new Promise((resolve, reject) => {
        const form = new FormData();
        form.append("file", file);
        const request = new XMLHttpRequest();
        request.open("POST", "/transcribe");
        request.upload.onprogress = (event) => {
          if (!event.lengthComputable) {
            setFileProgress(index, 15, "Uploading");
            return;
          }
          const percent = Math.round((event.loaded / event.total) * 100);
          setFileProgress(index, percent, `Uploading ${percent}%`);
        };
        request.onload = () => {
          let payload = {};
          try {
            payload = JSON.parse(request.responseText || "{}");
          } catch (error) {
            reject(new Error("Server returned an invalid response"));
            return;
          }

          if (request.status < 200 || request.status >= 300) {
            reject(new Error(payload.detail || "Transcription failed"));
            return;
          }
          resolve(payload);
        };
        request.onerror = () => reject(new Error("Network error"));
        request.send(form);
      });
    }

    function setFileProgress(index, percent, label) {
      const progress = $(`fileProgress-${index}`);
      const status = $(`fileStatus-${index}`);
      if (progress) {
        progress.style.width = `${Math.max(0, Math.min(percent, 100))}%`;
      }
      if (status && label) {
        status.textContent = label;
      }
    }

    function setFileResult(index, text, isError = false) {
      const target = $(`fileResult-${index}`);
      if (!target) return;
      target.classList.add("visible");
      target.classList.toggle("error", isError);
      target.textContent = text;
    }

    function scrollToPanel(id) {
      const target = $(id);
      if (!target) return;
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    async function refresh() {
      const [health, model, metricsText] = await Promise.all([
        fetch("/health").then((response) => response.json()),
        fetch("/model").then((response) => response.json()),
        fetch("/metrics").then((response) => response.text()),
      ]);
      const metrics = parseMetrics(metricsText);

      $("status").textContent = health.status === "ok" ? "Server OK" : health.status;
      $("subtitle").textContent = `${model.model} on ${model.device}`;
      $("queue").textContent = health.queue_size;
      $("requests").textContent = metrics.requests_total ?? 0;
      $("errors").textContent = metrics.errors_total ?? 0;
      $("rejected").textContent = metrics.rejected_requests_total ?? 0;
      $("timeouts").textContent = metrics.timeouts_total ?? 0;
      $("model").textContent = model.model;
      $("modelSource").textContent = model.model_is_local ? "Local CT2 path" : "Model name / HF id";
      $("device").textContent = model.device;
      $("compute").textContent = model.compute_type;
      $("pipeline").textContent = model.batched_pipeline ? "Batched" : "Standard";
      $("modelLanguage").textContent = model.language || "auto";
      $("modelTask").textContent = model.task || "transcribe";
      $("batch").textContent = model.max_batch_size;
      $("wait").textContent = `${model.max_wait_ms} ms`;
      $("queueLimit").textContent = model.queue_max_size;
      $("timeout").textContent = `${model.request_timeout_seconds} s`;
    }

    fileInput.addEventListener("change", () => {
      selectFiles(fileInput.files, true);
      fileInput.value = "";
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.add("active");
      });
    });

    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("active");
    });

    dropzone.addEventListener("drop", (event) => {
      event.preventDefault();
      dropzone.classList.remove("active");
      selectFiles(event.dataTransfer.files, true);
    });

    document.querySelectorAll(".nav-item[data-target]").forEach((item) => {
      item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach((navItem) => {
          navItem.classList.toggle("active", navItem === item);
        });
        scrollToPanel(item.dataset.target);
      });
    });

    $("openDocs").addEventListener("click", () => window.open("/docs", "_blank"));
    $("openMetrics").addEventListener("click", () => window.open("/metrics", "_blank"));
    $("openModel").addEventListener("click", () => window.open("/model", "_blank"));
    $("refreshScheduler").addEventListener("click", refresh);
    $("refresh").addEventListener("click", refresh);
    $("clearFile").addEventListener("click", () => {
      fileInput.value = "";
      selectFiles([]);
    });
    $("copyResult").addEventListener("click", async () => {
      if (!latestTranscription) return;
      await navigator.clipboard.writeText(latestTranscription);
      $("copyResult").textContent = "Copied";
      setTimeout(() => ($("copyResult").textContent = "Copy"), 1200);
    });
    $("clearResult").addEventListener("click", () => {
      latestTranscription = "";
      $("language").textContent = "-";
      $("duration").textContent = "-";
      setResult("");
      document.querySelectorAll(".file-result").forEach((item) => {
        item.classList.remove("visible", "error");
        item.textContent = "";
      });
    });

    $("form").addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!selectedFiles.length) return;

      submit.disabled = true;
      submit.textContent = "Running";
      setUploadProgress(0, `${selectedFiles.length} files queued`);
      setResult("");
      $("language").textContent = "-";
      $("duration").textContent = "-";

      try {
        const startedAt = performance.now();
        const results = await Promise.allSettled(
          selectedFiles.map((file, index) => transcribeWithProgress(file, index))
        );
        const elapsedSeconds = (performance.now() - startedAt) / 1000;
        const successfulResults = [];
        let failedCount = 0;

        results.forEach((resultItem, index) => {
          if (resultItem.status === "fulfilled") {
            const payload = resultItem.value;
            successfulResults.push(payload);
            setFileProgress(index, 100, "Completed");
            setFileResult(index, payload.text || "");
          } else {
            failedCount += 1;
            setFileProgress(index, 100, "Failed");
            setFileResult(index, resultItem.reason.message, true);
          }
        });

        setUploadProgress(
          100,
          `${successfulResults.length} completed, ${failedCount} failed`
        );
        result.classList.remove("empty");
        setResult(
          successfulResults
            .map((payload, index) => `#${index + 1}\\n${payload.text || ""}`)
            .join("\\n\\n")
        );
        $("language").textContent = summarizeLanguages(successfulResults);
        $("duration").textContent = successfulResults.length
          ? `${elapsedSeconds.toFixed(2)} s`
          : "-";
      } catch (error) {
        setUploadProgress(100, "Upload or transcription failed");
        setResult(error.message, true);
      } finally {
        submit.disabled = false;
        submit.textContent = "Transcribe";
        refresh();
      }
    });

    function summarizeLanguages(results) {
      const languages = [...new Set(results.map((item) => item.language).filter(Boolean))];
      return languages.length ? languages.join(", ") : "-";
    }

    selectFiles([]);
    refresh();
  </script>
</body>
</html>
"""
