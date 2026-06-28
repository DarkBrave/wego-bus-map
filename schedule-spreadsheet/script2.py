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
    # first stop per trip only (avoid overcounting stops)
    stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])
    first_stops = stop_times.groupby("trip_id", as_index=False).first()

    # convert time → minutes
    first_stops["minute"] = first_stops["arrival_time"].apply(parse_time_to_minutes)

    # merge route + direction
    df = first_stops.merge(
        trips[["trip_id", "route_id", "direction_id"]],
        on="trip_id",
        how="left"
    )

    # 5-minute bin
    df["bin_min"] = (df["minute"] // 5) * 5
    df["time"] = df["bin_min"].astype(int).apply(minutes_to_label)

    # create combined column: route + direction
    df["route_dir"] = (
        df["route_id"].astype(str) + " (" + df["direction_id"].astype(str) + ")"
    )

    # pivot
    grid = (
        df.groupby(["time", "route_dir"])
        .size()
        .unstack(fill_value=0)
    )

    # full day index
    full_times = [minutes_to_label(m) for m in range(0, 1440, 5)]
    grid = grid.reindex(full_times, fill_value=0)

    return grid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gtfs_folder")
    parser.add_argument("--out", default="gtfs_grid.csv")
    args = parser.parse_args()

    trips, stop_times = load_gtfs(args.gtfs_folder)

    print("Building inbound/outbound grid...")
    grid = build_grid(trips, stop_times)

    print("Saving...")

    if args.out.endswith(".xlsx"):
        grid.to_excel(args.out)
    else:
        grid.to_csv(args.out)

    print(f"Done → {args.out}")


if __name__ == "__main__":
    main()
