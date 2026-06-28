import pandas as pd
import argparse
import os


# ---------- time helpers ----------
def time_to_minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def minutes_to_label(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


# ---------- load ----------
def load_gtfs(folder):
    trips = pd.read_csv(os.path.join(folder, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(folder, "stop_times.txt"))
    calendar = pd.read_csv(os.path.join(folder, "calendar.txt"))
    return trips, stop_times, calendar


# ---------- build grid ----------
def build_grid(trips, stop_times, calendar):

    # -----------------------------------------
    # 1. FILTER TO CORRECT SERVICE PERIOD (85.*)
    # -----------------------------------------
    calendar = calendar[calendar["service_id"].str.startswith("85")]

    # -----------------------------------------
    # 2. FILTER TO TUESDAY SERVICE ONLY
    # -----------------------------------------
    weekday_service_ids = calendar[
        calendar["tuesday"] == 1
    ]["service_id"]

    trips = trips[trips["service_id"].isin(weekday_service_ids)]

    # clean duplicates
    trips = trips.drop_duplicates(subset=["trip_id"])

    # -----------------------------------------
    # 3. FIRST STOP ONLY PER TRIP
    # -----------------------------------------
    stop_times = stop_times.sort_values(["trip_id", "stop_sequence"])
    first_stops = stop_times.drop_duplicates(subset=["trip_id"], keep="first").copy()

    # use departure time (correct GTFS meaning)
    first_stops["minute"] = first_stops["departure_time"].apply(time_to_minutes)

    # -----------------------------------------
    # 4. JOIN ROUTE + DIRECTION
    # -----------------------------------------
    df = first_stops.merge(
        trips[["trip_id", "route_id", "direction_id"]],
        on="trip_id",
        how="inner"
    )

    df["direction_id"] = df["direction_id"].fillna(0).astype(int)

    # -----------------------------------------
    # 5. 5-MINUTE BINNING
    # -----------------------------------------
    df["bin"] = (df["minute"] // 5) * 5
    df["time"] = df["bin"].astype(int).apply(minutes_to_label)

    # -----------------------------------------
    # 6. ROUTE + DIRECTION LABEL
    # -----------------------------------------
    df["route_dir"] = (
        df["route_id"].astype(str)
        + " ("
        + df["direction_id"].astype(str)
        + ")"
    )

    # -----------------------------------------
    # 7. PIVOT GRID
    # -----------------------------------------
    grid = (
        df.groupby(["time", "route_dir"])
        .size()
        .unstack(fill_value=0)
    )

    # full day timeline
    full_times = [minutes_to_label(m) for m in range(0, 1440, 5)]
    grid = grid.reindex(full_times, fill_value=0)

    return grid


# ---------- main ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gtfs_folder")
    parser.add_argument("--out", default="gtfs_tuesday_grid.csv")
    args = parser.parse_args()

    trips, stop_times, calendar = load_gtfs(args.gtfs_folder)

    print("Building Tuesday schedule grid (85.* service)...")

    grid = build_grid(trips, stop_times, calendar)

    print("Saving output...")

    if args.out.endswith(".xlsx"):
        grid.to_excel(args.out)
    else:
        grid.to_csv(args.out)

    print(f"Done → {args.out}")


if __name__ == "__main__":
    main()
