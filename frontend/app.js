const API_BASE = "https://dzmitrymelnik.pythonanywhere.com";

document.getElementById("btn-weather").addEventListener("click", async () => {
  const city = document.getElementById("city").value.trim();
  const resultsEl = document.getElementById("results");
  resultsEl.innerHTML = "<p>Загрузка…</p>";

  if (!city) {
    resultsEl.innerHTML = "<p class='error'>Введите город.</p>";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/weather?city=${encodeURIComponent(city)}`);
    const data = await res.json();

    if (!res.ok) {
      resultsEl.innerHTML = `<p class="error">${data.error || res.status}</p>`;
      return;
    }

    let html = "";
    if (data.note) {
      html += `<p class="note">${data.note}</p>`;
    }
    if (data.sources && data.sources.length) {
      html += '<div class="cards">';
      data.sources.forEach((s) => {
        html += `
          <div class="card">
            <h3>${s.source || "Источник"}</h3>
            <p>Температура: ${s.temperature != null ? s.temperature + " °C" : "—"}</p>
            <p>Ветер: ${s.wind_speed != null ? s.wind_speed + " км/ч" : "—"}</p>
          </div>
        `;
      });
      html += "</div>";
    } else {
      html += "<p>Нет данных.</p>";
    }
    resultsEl.innerHTML = html;
  } catch (e) {
    resultsEl.innerHTML = `<p class="error">Ошибка: ${e.message}. Запущен ли бэкенд на порту 5000?</p>`;
  }
});