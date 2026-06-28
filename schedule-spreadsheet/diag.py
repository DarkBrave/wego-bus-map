import pandas as pd

trips = pd.read_csv("trips.txt")
stop_times = pd.read_csv("stop_times.txt")

print("stop_times rows:", len(stop_times))
print("unique stops:", stop_times["stop_id"].nunique())

print("sample stop_ids:")
print(stop_times["stop_id"].astype(str).head(20))
