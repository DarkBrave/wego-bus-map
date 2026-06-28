import pandas as pd
import argparse
import os


def parse_time_to_minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def minutes_to_label(mins: int) -> str:
    h = mins // 60
    m = mins % 60
    return f"{h:02d}:{m:02d}"


def load_gtfs(folder):
    trips = pd.read_csv(os.path.join(folder, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(folder, "stop_times.txt"))
    return trips, stop_times


def build_grid(trips, stop_times):
    # first stop per trip (avoid double counting)
    stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])
    first_stops = stop_times.groupby("trip_id", as_index=False).first()

    # convert time → minutes
    first_stops["minute"] = first_stops["arrival_time"].apply(parse_time_to_minutes)

    # route mapping
    df = first_stops.merge(trips[["trip_id", "route_id"]], on="trip_id", how="left")

    # force into 5-minute buckets
    df["bin_min"] = (df["minute"] // 5) * 5

    # convert to readable time labels
    df["time"] = df["bin_min"].astype(int).apply(minutes_to_label)

    # pivot: rows = time, cols = routes
    grid = (
        df.groupby(["time", "route_id"])
        .size()
        .unstack(fill_value=0)
    )

    # ensure full day coverage (00:00–23:55)
    full_times = [minutes_to_label(m) for m in range(0, 1440, 5)]
    grid = grid.reindex(full_times, fill_value=0)

    return grid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gtfs_folder")
    parser.add_argument("--out", default="gtfs_grid.csv")
    args = parser.parse_args()

    trips, stop_times = load_gtfs(args.gtfs_folder)

    print("Building grid...")
    grid = build_grid(trips, stop_times)

    print("Saving...")

    if args.out.endswith(".xlsx"):
        grid.to_excel(args.out)
    else:
        grid.to_csv(args.out)

    print(f"Done → {args.out}")


if __name__ == "__main__":
    main()
