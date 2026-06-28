import pandas as pd
import argparse
import os


# ---------------- time helpers ----------------
def time_to_minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def minutes_to_label(m: float) -> str:
    m = int(m)
    return f"{m // 60:02d}:{m % 60:02d}"


# ---------------- load GTFS ----------------
def load_gtfs(folder):
    trips = pd.read_csv(os.path.join(folder, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(folder, "stop_times.txt"))
    calendar = pd.read_csv(os.path.join(folder, "calendar.txt"))
    return trips, stop_times, calendar


# ---------------- build timetable ----------------
def build_timetable(trips, stop_times, calendar, stop_id):

    # -----------------------------------
    # 1. USE ONLY 85.* (Jan–July block)
    # -----------------------------------
    calendar = calendar[calendar["service_id"].astype(str).str.startswith("85")]

    # -----------------------------------
    # 2. TUESDAY SERVICE ONLY
    # -----------------------------------
    service_ids = calendar[calendar["tuesday"] == 1]["service_id"]
    trips = trips[trips["service_id"].isin(service_ids)]

    trips = trips.drop_duplicates(subset=["trip_id"])

    # -----------------------------------
    # 3. FILTER STOP
    # -----------------------------------
    stop_times = stop_times[stop_times["stop_id"].astype(str) == str(stop_id)].copy()

    if stop_times.empty:
        raise ValueError(f"No stop_times found for stop_id={stop_id}")

    # -----------------------------------
    # 4. JOIN TRIPS
    # -----------------------------------
    df = stop_times.merge(
        trips[["trip_id", "route_id", "direction_id"]],
        on="trip_id",
        how="inner"
    )

    df["direction_id"] = df["direction_id"].fillna(0).astype(int)

    # -----------------------------------
    # 5. TIME PROCESSING
    # -----------------------------------
    df["minute"] = df["departure_time"].apply(time_to_minutes)
    df["time"] = df["minute"].apply(minutes_to_label)

    # -----------------------------------
    # 6. ROUTE LABEL
    # -----------------------------------
    df["route_dir"] = (
        df["route_id"].astype(str)
        + " ("
        + df["direction_id"].astype(str)
        + ")"
    )

    # -----------------------------------
    # 7. SORT LIKE REAL TIMETABLE
    # -----------------------------------
    df = df.sort_values("minute")

    timetable = df[["time", "route_dir"]].reset_index(drop=True)

    return timetable


# ---------------- main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gtfs_folder")
    parser.add_argument("stop_id")
    parser.add_argument("--out", default="stop_timetable.csv")
    args = parser.parse_args()

    trips, stop_times, calendar = load_gtfs(args.gtfs_folder)

    print(f"Building timetable for stop: {args.stop_id}")

    timetable = build_timetable(trips, stop_times, calendar, args.stop_id)

    print("Saving...")

    if args.out.endswith(".xlsx"):
        timetable.to_excel(args.out, index=False)
    else:
        timetable.to_csv(args.out, index=False)

    print(f"Done → {args.out}")


if __name__ == "__main__":
    main()
