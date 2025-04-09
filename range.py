import pandas as pd

df = pd.read_csv("base_demo.csv")

# Проверяем максимальные значения в числовых колонках
columns_to_check = ["year-from", "year-to", "engine-power", "engine-volume"]

for col in columns_to_check:
    if col in df.columns:
        print(f"{col}: max = {df[col].max()} min = {df[col].min()}")
