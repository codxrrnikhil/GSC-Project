const form = document.getElementById("similarity-form");
const resultEl = document.getElementById("result");
const historyBody = document.getElementById("history-body");
const refreshBtn = document.getElementById("refresh-history");

async function fetchDetectionHistory(baseUrl) {
  const response = await fetch(`${baseUrl}/api/v1/pipeline/detections`);
  if (!response.ok) {
    throw new Error(`Failed to load detections: ${response.status}`);
  }
  return response.json();
}

function renderHistory(rows) {
  historyBody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><a href="${row.url}" target="_blank" rel="noreferrer">${row.url}</a></td>
      <td>${Number(row.similarity_score).toFixed(4)}</td>
      <td>${row.matched_asset_id ?? "-"}</td>
      <td>${row.timestamp ?? "-"}</td>
    `;
    historyBody.appendChild(tr);
  }
}

async function refreshHistory() {
  const baseUrl = document.getElementById("backend-url").value.trim();
  try {
    const rows = await fetchDetectionHistory(baseUrl);
    renderHistory(rows);
  } catch (error) {
    resultEl.textContent = error.message;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const baseUrl = document.getElementById("backend-url").value.trim();
  const articleUrl = document.getElementById("article-url").value.trim();
  const platform = document.getElementById("platform").value.trim();
  const fileInput = document.getElementById("media-file");
  const file = fileInput.files?.[0];

  if (!file) {
    resultEl.textContent = "Please choose a media file.";
    return;
  }

  const formData = new FormData();
  formData.append("url", articleUrl);
  formData.append("platform", platform);
  formData.append("file", file);

  resultEl.textContent = "Running similarity detection...";
  try {
    const response = await fetch(`${baseUrl}/api/v1/pipeline/similarity`, {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || `Request failed (${response.status})`);
    }

    resultEl.textContent = JSON.stringify(payload, null, 2);
    await refreshHistory();
  } catch (error) {
    resultEl.textContent = error.message;
  }
});

refreshBtn.addEventListener("click", refreshHistory);
refreshHistory();
