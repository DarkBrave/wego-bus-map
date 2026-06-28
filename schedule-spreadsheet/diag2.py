import pandas as pd

stop_times = pd.read_csv("stop_times.txt")

print(stop_times[stop_times["stop_id"] == "MCC5_8"].head())
