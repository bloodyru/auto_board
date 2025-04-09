"""С помощью этого скрипта надо импортировать данные из csv в таблицу с сайта базы данных марок авто"""
import pandas as pd
import psycopg2
import re
import numpy as np

# 🔹 Подключение к PostgreSQL
try:
    conn = psycopg2.connect(
        dbname="auto_board",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
except psycopg2.OperationalError as e:
    print(f"❌ Ошибка подключения к базе данных: {e}")
    exit(1)

# 🔹 Читаем CSV
csv_file = "base.csv"
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"❌ Файл {csv_file} не найден.")
    exit(1)

# 🔹 Приводим названия столбцов к корректному формату
# Удаляем спецсимволы и приводим к нижнему регистру
df.columns = [
    f"col_{col}" if re.match(r"^\d", col) else re.sub(r'\W+', '_', col).lower()
    for col in df.columns
]

# 🔹 Преобразуем все данные в строковый формат и заменяем NaN/None/False/True на корректные строки
df = df.astype(str).replace({"nan": "", "None": "", "False": "0", "True": "1"})

# 🔹 Удаляем `.0` из целых чисел, сохранённых как строки, и обрабатываем вещественные числа
for col in df.columns:
    df[col] = df[col].apply(lambda x: x[:-2] if x.endswith(".0") else x)
    df[col] = df[col].replace("", "NULL")  # Заменяем пустые строки на NULL для PostgreSQL
    df[col] = df[col].apply(lambda x: x.replace(",", ".") if re.match(r"^\d+[,.]\d+$", x) else x)  # Преобразуем 20,3 в 20.3
    df[col] = df[col].apply(lambda x: "NULL" if x == "" else x)
    df[col] = df[col].apply(lambda x: str(int(float(x))) if re.match(r"^\d+\.\d+$", x) else x)  # Преобразуем "21.5" в "21"

# 🔹 Определяем SQL-тип данных (все данные - TEXT)
column_types = {col: "TEXT" for col in df.columns}

# 🔹 Формируем SQL-запрос для создания таблицы
try:
    table_name = "cars_data_test"
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    create_table_query += ",\n".join([f"    \"{col}\" {col_type}" for col, col_type in column_types.items()])
    create_table_query += "\n);"
    cursor.execute(create_table_query)
    conn.commit()
    print("✅ Таблица успешно создана!")
except psycopg2.Error as e:
    print(f"❌ Ошибка создания таблицы: {e}")
    exit(1)

# 🔹 Загружаем данные в PostgreSQL
columns = ", ".join([f"\"{col}\"" for col in df.columns])
placeholders = ", ".join(["%s"] * len(df.columns))
insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

for _, row in df.iterrows():
    try:
        row = [None if value == "NULL" else value for value in row]  # Преобразуем "NULL" обратно в None
        cursor.execute(insert_query, tuple(row))
    except psycopg2.Error as e:
        conn.rollback()
        print(f"⚠ Ошибка вставки: {e}")
        print(f"Строка с ошибкой: {row}")

conn.commit()
cursor.close()
conn.close()

print("✅ Данные успешно загружены в PostgreSQL!")
