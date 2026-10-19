import pandas as pd

df_2026 = pd.read_csv("2026_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2025 = pd.read_csv("2025_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2024 = pd.read_csv("2024_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2023 = pd.read_csv("2023_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)

df_storico = pd.concat([df_2023, df_2024, df_2025], ignore_index=True)

columns = list(df_2026.columns)
print(columns)