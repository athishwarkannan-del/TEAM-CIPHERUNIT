"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { AlertTriangle, MapPin as MapPinIcon, Clock, Navigation } from "lucide-react";
import { fetchGeo } from "@/lib/api";
import type { GeoIntelligenceResponse } from "@/lib/types";

// Dynamic import for Leaflet (SSR incompatible)
const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then((m) => m.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false });
const Polyline = dynamic(() => import("react-leaflet").then((m) => m.Polyline), { ssr: false });

// City coordinates for impossible travel arcs
const cityCoords: Record<string, [number, number]> = {
  Mumbai: [19.076, 72.8777],
  Delhi: [28.7041, 77.1025],
  Bengaluru: [12.9716, 77.5946],
  Hyderabad: [17.385, 78.4867],
  Chennai: [13.0827, 80.2707],
  Kolkata: [22.5726, 88.3639],
  Pune: [18.5204, 73.8567],
  Jaipur: [26.9124, 75.7873],
};

export default function GeoPage() {
  const [data, setData] = useState<GeoIntelligenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [leafletReady, setLeafletReady] = useState(false);

  useEffect(() => {
    // Load leaflet CSS
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
    document.head.appendChild(link);
    setLeafletReady(true);

    fetchGeo().then((res) => {
      setData(res.data);
      setLoading(false);
    });
  }, []);

  if (loading || !data || !leafletReady) {
    return (
      <div className="space-y-5 animate-fade-in">
        <div className="skeleton h-12 rounded-xl" />
        <div className="skeleton h-[550px] rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in">
      <div className="page-header">
        <p className="page-subtitle">
          Geographic fraud density heatmaps and impossible travel velocity alerts across India
        </p>
      </div>

      {/* Map + Sidebar */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_360px]">
        {/* Map */}
        <div className="glass-card overflow-hidden" style={{ height: 560 }}>
          <MapContainer
            center={[20.5937, 78.9629]}
            zoom={5}
            scrollWheelZoom={true}
            style={{ height: "100%", width: "100%" }}
            className="rounded-xl"
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Regional Clusters */}
            {data.regional_clusters.map((cluster) => (
              <CircleMarker
                key={cluster.city}
                center={[cluster.lat, cluster.lng]}
                radius={Math.max(12, cluster.mule_count * 0.8)}
                pathOptions={{
                  color: cluster.mule_count >= 25 ? "#ef4444" : cluster.mule_count >= 15 ? "#f59e0b" : "#3b82f6",
                  fillColor: cluster.mule_count >= 25 ? "#ef4444" : cluster.mule_count >= 15 ? "#f59e0b" : "#3b82f6",
                  fillOpacity: 0.3,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="text-center">
                    <p className="text-sm font-bold">{cluster.city}</p>
                    <p className="text-xs">{cluster.mule_count} Active Mules</p>
                  </div>
                </Popup>
              </CircleMarker>
            ))}

            {/* Impossible Travel Arcs */}
            {data.impossible_travel_alerts.map((alert, i) => {
              const origin = cityCoords[alert.origin];
              const dest = cityCoords[alert.destination];
              if (!origin || !dest) return null;
              return (
                <Polyline
                  key={i}
                  positions={[origin, dest]}
                  pathOptions={{
                    color: "#ef4444",
                    weight: 2,
                    dashArray: "8, 8",
                    opacity: 0.7,
                  }}
                />
              );
            })}
          </MapContainer>
        </div>

        {/* Right Panel */}
        <div className="space-y-4">
          {/* Legend */}
          <div className="glass-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-white">Map Legend</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-500/40 ring-2 ring-red-500" />
                <span className="text-slate-300">Critical Zone (25+ mules)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-amber-500/40 ring-2 ring-amber-500" />
                <span className="text-slate-300">High Risk Zone (15-24)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-blue-500/40 ring-2 ring-blue-500" />
                <span className="text-slate-300">Moderate Zone (&lt;15)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-4 w-6 border-t-2 border-dashed border-red-500" />
                <span className="text-slate-300">Impossible Travel Arc</span>
              </div>
            </div>
          </div>

          {/* Impossible Travel Alerts */}
          <div className="glass-card p-4">
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
              <AlertTriangle className="h-4 w-4 text-red-400" />
              Impossible Travel Alerts
            </h3>
            <div className="space-y-3">
              {data.impossible_travel_alerts.map((alert, i) => (
                <div key={i} className="glass-card-sm p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-accent-glow">{alert.account_number}</span>
                    <span className="badge bg-red-500/15 text-red-400 border-red-500/30">FLAGGED</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-slate-300">
                    <MapPinIcon className="h-3 w-3 text-blue-400" />
                    <span>{alert.origin}</span>
                    <Navigation className="h-3 w-3 text-red-400" />
                    <span>{alert.destination}</span>
                  </div>
                  <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {alert.time_gap_minutes} min gap
                    </span>
                    <span>{alert.distance_km.toLocaleString()} km</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Regional Summary */}
          <div className="glass-card p-4">
            <h3 className="mb-3 text-sm font-semibold text-white">Regional Summary</h3>
            <div className="space-y-2">
              {data.regional_clusters
                .sort((a, b) => b.mule_count - a.mule_count)
                .map((cluster) => (
                  <div key={cluster.city} className="flex items-center justify-between text-xs">
                    <span className="text-slate-300">{cluster.city}</span>
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-navy-700">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${(cluster.mule_count / 34) * 100}%`,
                            backgroundColor: cluster.mule_count >= 25 ? "#ef4444" : cluster.mule_count >= 15 ? "#f59e0b" : "#3b82f6",
                          }}
                        />
                      </div>
                      <span className="w-6 text-right font-medium text-white">{cluster.mule_count}</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
