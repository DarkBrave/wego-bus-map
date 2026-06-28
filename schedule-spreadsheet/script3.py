import pandas as pd
import argparse
import os


# ---------- time parsing ----------
def time_to_minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def minutes_to_label(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


# ---------- load GTFS ----------
def load_gtfs(folder):
    trips = pd.read_csv(os.path.join(folder, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(folder, "stop_times.txt"))
    return trips, stop_times


# ---------- core build ----------
def build_grid(trips, stop_times):

    # clean duplicates (important for messy feeds)
    trips = trips.drop_duplicates(subset=["trip_id"])

    stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])

    # TRUE first stop per trip
    first_stops = stop_times.drop_duplicates(subset=["trip_id"], keep="first").copy()

    # IMPORTANT: use departure_time, not arrival_time
    first_stops["minute"] = first_stops["departure_time"].apply(time_to_minutes)

    # merge route + direction
    df = first_stops.merge(
        trips[["trip_id", "route_id", "direction_id"]],
        on="trip_id",
        how="left"
    )

    # 5-minute bin
    df["bin"] = (df["minute"] // 5) * 5
    df["time"] = df["bin"].astype(int).apply(minutes_to_label)

    # combine route + direction
    df["route_dir"] = (
        df["route_id"].astype(str) + " (" + df["direction_id"].fillna(0).astype(int).astype(str) + ")"
    )

    # pivot table
    grid = (
        df.groupby(["time", "route_dir"])
        .size()
        .unstack(fill_value=0)
    )

    # full day coverage
    full_times = [minutes_to_label(m) for m in range(0, 1440, 5)]
    grid = grid.reindex(full_times, fill_value=0)
    print(df.groupby("route_dir").size().sort_values(ascending=False).head(10))

    return grid


# ---------- main ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gtfs_folder")
    parser.add_argument("--out", default="gtfs_grid.csv")
    args = parser.parse_args()

    trips, stop_times = load_gtfs(args.gtfs_folder)

    print("Building corrected GTFS grid...")
    grid = build_grid(trips, stop_times)

    print("Saving output...")

    if args.out.endswith(".xlsx"):
        grid.to_excel(args.out)
    else:
        grid.to_csv(args.out)

    print(f"Done → {args.out}")


if __name__ == "__main__":
    main()
