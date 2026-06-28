import React, { useRef, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import ReactLeafletDriftMarker from 'react-leaflet-drift-marker';
import L from 'leaflet';
import VehicleMarkerPopup from './VehicleMarkerPopup';
import VehicleMarkerTooltip from './VehicleMarkerTooltip';
import '../lib/leaflet-rotated-marker';
import busMarkerImage from '../resources/bus.svg';
import busOfflineMarkerImage from '../resources/bus-offline.svg';
import trainMarkerImage from '../resources/train.svg';
import trainOfflineMarkerImage from '../resources/train-offline.svg';
import { getJSON } from '../util';
import './VehicleMarker.scss';

const routeIcons = import.meta.glob('../resources/routes/*.svg', {
  eager: true,
  import: 'default',
});

function getRouteIcon(routeNumber) {
  const path = `../resources/routes/${routeNumber}.svg`;
  return routeIcons[path];
}

const GTFS_BASE_URL = import.meta.env.VITE_GTFS_BASE_URL;

function VehicleMarker({
                         vehiclePositionData,
                         route,
                         agency,
                         tripUpdate,
                         shapeSetter,
                         stopSetter,
                         alerts,
                       }) {
  const [trip, setTripData] = useState({});
  const marker = useRef(null);

  const isOffline = route === undefined || !route.route_gid;

  let iconUrl = busMarkerImage;

  if (route?.route_type === '2') {
    iconUrl = isOffline ? trainOfflineMarkerImage : trainMarkerImage;
  } else if (route?.route_short_name) {
    const routeIcon = getRouteIcon(route.route_short_name);
    iconUrl = routeIcon || (isOffline ? busOfflineMarkerImage : busMarkerImage);
  } else {
    iconUrl = isOffline ? busOfflineMarkerImage : busMarkerImage;
  }

  const bearing = vehiclePositionData.vehicle.position.bearing ?? 0;

  // ---- ICON (DivIcon so we can overlay triangle) ----
  const icon = L.divIcon({
    className: 'vehicle-marker',
    html: `
      <div class="vehicle-wrapper">
        <img src="${iconUrl}" class="vehicle-icon" />
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  // ---- Apply CSS variable safely ----
  useEffect(() => {
    if (!marker.current) return;

    const updateBearing = () => {
      const el = marker.current?.getElement?.();
      if (!el) return false;

      el.style.setProperty('--bearing', `${bearing}deg`);
      return true;
    };

    // try immediately
    if (updateBearing()) return;

    // fallback: wait until Leaflet attaches DOM
    const interval = setInterval(() => {
      if (updateBearing()) {
        clearInterval(interval);
      }
    }, 16);

    return () => clearInterval(interval);
  }, [bearing]);

  // ---- opacity for stale vehicles ----
  let opacity = 1.0;
  if ((Date.now() / 1000) - vehiclePositionData.vehicle.timestamp > 120) {
    opacity = 0.25;
  }

  // ---- click handler ----
  const showTripDetails = () => {
    if (!vehiclePositionData.vehicle.trip) return;

    getJSON(`${GTFS_BASE_URL}/trips/${vehiclePositionData.vehicle.trip?.trip_id}.json`)
      .then((trip) => {
        trip.shape.route_color = route.route_color;
        shapeSetter([trip.shape]);
        stopSetter(trip.stop_times);
        return trip;
      })
      .then((data) => setTripData(data));
  };

  return (
    <ReactLeafletDriftMarker
      ref={marker}
      duration={1000}
      eventHandlers={{ click: showTripDetails }}
      position={[
        vehiclePositionData.vehicle.position.latitude,
        vehiclePositionData.vehicle.position.longitude,
      ]}
      icon={icon}
      opacity={opacity}
      zIndexOffset={100}
      className="vehicle-marker"
    >
      <VehicleMarkerPopup
        vehiclePositionData={vehiclePositionData}
        route={route}
        agency={agency}
        trip={trip}
        tripUpdate={tripUpdate}
        alerts={alerts}
      />
      <VehicleMarkerTooltip
        vehiclePositionData={vehiclePositionData}
        route={route}
        alerts={alerts}
      />
    </ReactLeafletDriftMarker>
  );
}

VehicleMarker.propTypes = {
  vehiclePositionData: PropTypes.object.isRequired,
  route: PropTypes.object.isRequired,
  agency: PropTypes.object.isRequired,
  shapeSetter: PropTypes.func.isRequired,
  stopSetter: PropTypes.func.isRequired,
  tripUpdate: PropTypes.object,
  alerts: PropTypes.array,
};

VehicleMarker.defaultProps = {
  tripUpdate: {},
  alerts: [],
};

export default VehicleMarker;
