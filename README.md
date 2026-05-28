# Лабораторная работа №14: Разработка конвейеров обработки данных на Python и Go

**Студент:** Азаров Алексей Семенович
**Группа:** 221331-01
**Вариант:** 2
**Тема:** Анализ погодных данных OpenWeatherMap API
**Сложность:** Повышенная

## Описание

ETL/ELT-конвейер для сбора, обработки и анализа погодных данных с OpenWeatherMap API. Сборщик на Go параллельно опрашивает API для 10 городов, данные проходят через цепочку: JSON → Polars → Parquet → DuckDB → визуализация.

## Архитектура

```
Go-сборщик → JSON → Polars (очистка) → Parquet → DuckDB (SQL) → Plotly (графики)
```

## Структура проекта

| Компонент | Язык | Назначение |
|:----------|:-----|:-----------|
| **collector/** | Go | Параллельный сбор данных из OpenWeatherMap API |
| **analysis/** | Python | Импорт, очистка, агрегация, DuckDB, визуализация |
| **data/** | - | Хранилище JSON и Parquet файлов |
| **docs/** | - | Сгенерированные HTML/PNG графики |
| **diagrams/** | - | PlantUML диаграммы архитектуры |

## Запуск

### Требования

- Go 1.21+
- Python 3.12+
- API ключ OpenWeatherMap (https://openweathermap.org/api)

### Установка

```bash
pip install -r requirements.txt
cd collector && go mod tidy
```

### Сбор данных

```bash
export OWM_API_KEY=your_api_key_here
cd collector && go run main.go
```

### Анализ данных

```bash
cd analysis
python run_pipeline.py
```

### Docker

```bash
export OWM_API_KEY=your_api_key_here
docker-compose up --build
```

## Компоненты конвейера

### 1. Go-сборщик
- Горутины для параллельного опроса API 10 городов
- Буферизированный канал (100 записей)
- Пакетная запись (5 записей или 10 секунд)
- Graceful shutdown (SIGINT/SIGTERM)

### 2. Импорт в Polars
- Чтение JSON-файлов в DataFrame
- Вывод первых 5 строк и базовой статистики

### 3. Очистка данных
- Удаление дубликатов
- Обработка пропусков
- Фильтрация некорректных температур
- Приведение типов

### 4. Агрегационный анализ
- Группировка по городам: AVG, MIN, MAX температуры
- Сводка по погодным условиям

### 5. Сохранение в Parquet
- Сжатие zstd
- Оптимизация для аналитики

### 6. DuckDB анализ
- SQL-запрос с фильтрацией, группировкой, сортировкой
- Сравнение производительности с Polars

### 7. Визуализация
- Столбчатая диаграмма температур по городам
- Scatter plot (температура vs влажность)
- Круговая диаграмма погодных условий

## Примеры SQL-запросов

```sql
SELECT
    city,
    AVG(temp) as avg_temp,
    MIN(temp) as min_temp,
    MAX(temp) as max_temp,
    COUNT(*) as measurements
FROM 'data/weather_clean.parquet'
WHERE temp > -20 AND temp < 45
GROUP BY city
ORDER BY avg_temp DESC;
```
