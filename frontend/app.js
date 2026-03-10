const API_BASE = "https://dzmitrymelnik.pythonanywhere.com";

function parseNum(val, min, max) {
  const n = Number(val);
  if (Number.isNaN(n)) return null;
  if (n < min || n > max) return null;
  return n;
}

document.getElementById("btn-weather").addEventListener("click", async () => {
  const city = document.getElementById("city").value.trim();
  const latVal = document.getElementById("lat").value;
  const lonVal = document.getElementById("lon").value;
  const resultsEl = document.getElementById("results");
  resultsEl.innerHTML = "<p>Загрузка…</p>";
  document.getElementById("current-weather-section").removeAttribute("aria-hidden");

  const lat = parseNum(latVal, -90, 90);
  const lon = parseNum(lonVal, -180, 180);

  let url;
  if (lat !== null && lon !== null) {
    url = `${API_BASE}/api/weather?lat=${lat}&lon=${lon}`;
  } else if (city) {
    url = `${API_BASE}/api/weather?city=${encodeURIComponent(city)}`;
  } else {
    resultsEl.innerHTML = "<p class='error'>Введите город или координаты (широта и долгота).</p>";
    return;
  }

  if ((latVal || lonVal) && (lat === null || lon === null)) {
    resultsEl.innerHTML = "<p class='error'>Широта от -90 до 90, долгота от -180 до 180.</p>";
    return;
  }

  try {
    const res = await fetch(url);
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
      data.sources.forEach((s, index) => {
        const isPrimary = index === 0 && (s.source || "").toLowerCase().includes("dwd");
        html += `
          <div class="card ${isPrimary ? "card-primary" : ""}">
            <h3>${s.source || "Источник"}${isPrimary ? ' <span class="badge">основной</span>' : ""}</h3>
            <p>Температура: ${s.temperature != null ? s.temperature + " °C" : "—"}</p>
            <p>Ветер: ${s.wind_speed != null ? s.wind_speed + " м/с" : "—"}</p>
            ${s.wind_direction != null ? `<p>Направление: ${s.wind_direction}°</p>` : ""}
            ${s.wind_gusts != null ? `<p>Порывы: ${s.wind_gusts} м/с</p>` : ""}
            ${s.error ? `<p class="error">${s.error}</p>` : ""}
          </div>
        `;
      });
      html += "</div>";
    } else {
      html += "<p>Нет данных.</p>";
    }
    resultsEl.innerHTML = html;
  } catch (e) {
    resultsEl.innerHTML = `<p class="error">Ошибка: ${e.message}</p>`;
  }
});

// Прогноз на неделю
document.getElementById("btn-forecast").addEventListener("click", async () => {
  const city = document.getElementById("city").value.trim();
  const latVal = document.getElementById("lat").value;
  const lonVal = document.getElementById("lon").value;
  const forecastSection = document.getElementById("forecast-section");
  const daysEl = document.getElementById("forecast-days");
  const windEl = document.getElementById("wind-by-height");

  const lat = parseNum(latVal, -90, 90);
  const lon = parseNum(lonVal, -180, 180);

  let url;
  if (lat !== null && lon !== null) {
    url = `${API_BASE}/api/forecast?lat=${lat}&lon=${lon}&days=7`;
  } else if (city) {
    url = `${API_BASE}/api/forecast?city=${encodeURIComponent(city)}&days=7`;
  } else {
    daysEl.innerHTML = "<p class='error'>Введите город или координаты.</p>";
    windEl.innerHTML = "";
    forecastSection.removeAttribute("aria-hidden");
    return;
  }

  if ((latVal || lonVal) && (lat === null || lon === null)) {
    daysEl.innerHTML = "<p class='error'>Широта от -90 до 90, долгота от -180 до 180.</p>";
    windEl.innerHTML = "";
    forecastSection.removeAttribute("aria-hidden");
    return;
  }

  daysEl.innerHTML = "<p>Загрузка…</p>";
  windEl.innerHTML = "";
  forecastSection.removeAttribute("aria-hidden");

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (!res.ok) {
      daysEl.innerHTML = `<p class="error">${data.error || res.status}</p>`;
      return;
    }

    if (data.error && (!data.daily || data.daily.length === 0)) {
      daysEl.innerHTML = `<p class="error">${data.error}</p>`;
      return;
    }

    let daysHtml = "";
    if (data.forecast_note) {
      daysHtml += `<p class="note">${data.forecast_note}</p>`;
    }
    if (data.daily && data.daily.length) {
      daysHtml = '<div class="forecast-cards">';
      data.daily.forEach((d) => {
        const dateStr = d.date ? new Date(d.date).toLocaleDateString("ru-RU", { weekday: "short", day: "numeric", month: "short" }) : "";
        daysHtml += `
          <div class="card forecast-card">
            <h3>${dateStr}</h3>
            <p>Макс: ${d.temperature_2m_max != null ? d.temperature_2m_max + " °C" : "—"}</p>
            <p>Мин: ${d.temperature_2m_min != null ? d.temperature_2m_min + " °C" : "—"}</p>
            <p>Ветер макс: ${d.wind_speed_10m_max != null ? d.wind_speed_10m_max + " м/с" : "—"}</p>
            <p>Порывы: ${d.wind_gusts_10m_max != null ? d.wind_gusts_10m_max + " м/с" : "—"}</p>
            <p>Направление: ${d.wind_direction_10m_dominant != null ? d.wind_direction_10m_dominant + "°" : "—"}</p>
          </div>
        `;
      });
      daysHtml += "</div>";
    } else {
      daysHtml = "<p>Нет данных по дням.</p>";
    }
    daysEl.innerHTML = daysHtml;

    if (data.wind_by_height && data.wind_by_height.length) {
      let windHtml = '<table class="wind-table"><thead><tr><th>Высота</th><th>Скорость, м/с</th><th>Направление, °</th></tr></thead><tbody>';
      data.wind_by_height.forEach((w) => {
        windHtml += `<tr><td>${w.height_label}</td><td>${w.speed != null ? w.speed : "—"}</td><td>${w.direction != null ? w.direction : "—"}</td></tr>`;
      });
      windHtml += "</tbody></table>";
      windEl.innerHTML = windHtml;
    } else {
      windEl.innerHTML = "<p>Нет данных по ветру по высотам.</p>";
    }
  } catch (e) {
    daysEl.innerHTML = `<p class="error">Ошибка: ${e.message}</p>`;
  }
});