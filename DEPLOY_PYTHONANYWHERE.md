# Деплой на PythonAnywhere: 3 источника погоды (включая DWD ICON)

Чтобы в ответе `/api/weather` было **три** источника (DWD ICON, Open-Meteo, OpenWeatherMap), на сервере должны быть актуальные файлы.

## Обязательные файлы для трёх источников

- `backend/app.py` — маршруты `/api/weather` и `/api/forecast`
- `backend/services/aggregator.py` — вызывает DWD ICON, Open-Meteo, OpenWeatherMap (именно в таком порядке)
- `backend/services/dwd_icon.py` — **обязателен**; без него будет ошибка импорта и только 2 источника или 500
- `backend/services/geocoding.py` — для поиска по городу
- `backend/services/open_meteo.py` — текущая погода и fallback прогноза
- `backend/services/openweather.py` — текущая погода

## Шаги после обновления файлов

1. В консоли: `cd ~/weather-mvp` (или ваш путь к проекту).
2. Обновить код: `git pull origin main` (или загрузить перечисленные файлы вручную).
3. Установить зависимости при необходимости:  
   `pip install -r backend/requirements.txt --user`
4. В разделе **Web** на PythonAnywhere нажать **Reload** для вашего приложения.

## Проверка

Откройте в браузере:

`https://ваш-логин.pythonanywhere.com/api/weather?lat=53.9&lon=27.5`

В JSON в `sources` должно быть **3** элемента. Первый — `"source": "DWD ICON"` (с данными или с полем `"error"`, если запрос к DWD не удался).

Если по-прежнему только 2 источника — на сервере всё ещё старая версия `aggregator.py` или отсутствует файл `backend/services/dwd_icon.py`.

---

## Корректный город и отображение места (геокодинг)

Чтобы при вводе города (Минск, Москва и т.д.) подставлялись **правильные координаты** и в ответе было **найденное место** для надписи «Погода для: …», на сервере должна быть актуальная версия:

- `backend/services/geocoding.py` — с функциями `geocode_first_with_location` и сортировкой по населению (`_sort_by_population`)
- `backend/app.py` — при запросе по `city` вызывается `geocode_first_with_location`, в ответ добавляется объект `location`

### Как проверить, что бэкенд обновлён

Выполните в терминале (подставьте свой домен):

```bash
curl -s "https://ВАШ_ЛОГИН.pythonanywhere.com/api/weather?city=Minsk"
```

- **Если в JSON есть поле `"location"`** с `name`, `country`, `latitude`, `longitude` — бэкенд обновлён, город и координаты работают как задумано.
- **Если в JSON только `"sources"`**, без `"location"` — на PythonAnywhere всё ещё старая версия. Нужно снова выполнить **Обновить код** (git pull) и **Reload** в разделе Web.
