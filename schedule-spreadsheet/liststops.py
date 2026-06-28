import pandas as pd
import argparse
import os


def load_gtfs(folder):
    routes = pd.read_csv(os.path.join(folder, "routes.txt"))
    trips = pd.read_csv(os.path.join(folder, "trips.txt"))
    stop_times = pd.read_csv(os.path.join(folder, "stop_times.txt"))
    stops = pd.read_csv(os.path.join(folder, "stops.txt"))
    return routes, trips, stop_times, stops


def main():
    parser = argparse.ArgumentParser(description="List all stops for a GTFS route")
    parser.add_argument("gtfs_folder")
    parser.add_argument("route_id")
    args = parser.parse_args()

    routes, trips, stop_times, stops = load_gtfs(args.gtfs_folder)

    # Find trips on this route
    route_trips = trips[trips["route_id"].astype(str) == str(args.route_id)]

    if route_trips.empty:
        print(f"No trips found for route {args.route_id}")
        return

    # Prefer direction 0 if available
    if "direction_id" in route_trips.columns:
        dir0 = route_trips[route_trips["direction_id"] == 0]
        if not dir0.empty:
            route_trips = dir0

    # Use the first trip
    trip_id = route_trips.iloc[0]["trip_id"]

    trip_stop_times = (
        stop_times[stop_times["trip_id"] == trip_id]
        .sort_values("stop_sequence")
    )

    result = trip_stop_times.merge(
        stops[["stop_id", "stop_name"]],
        on="stop_id",
        how="left"
    )

    print(f"\nRoute {args.route_id}")
    print(f"Trip used: {trip_id}\n")

    for _, row in result.iterrows():
        print(
            f"{int(row['stop_sequence']):3d}. "
            f"{row['stop_name']} ({row['stop_id']})"
        )


if __name__ == "__main__":
    main()
