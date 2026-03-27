/**
 * Red Zone Heatmap Component
 * Predictive maintenance visualization for high-failure areas
 */

import { useEffect, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { MapContainer, TileLayer, Circle, Popup, useMap } from 'react-leaflet';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, 
  Zap, 
  Droplets, 
  Trash2,
  Filter,
  RefreshCw,
  TrendingUp,
  MapPin,
  Info
} from 'lucide-react';
import type { RedZone, HeatmapPoint } from '@/types';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import 'leaflet/dist/leaflet.css';

// Map controller component
function MapController({ 
  center, 
  zoom 
}: { 
  center: [number, number]; 
  zoom: number;
}) {
  const map = useMap();
  
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  
  return null;
}

export default function RedZoneHeatmap() {
  const [redZones, setRedZones] = useState<RedZone[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedRisk, setSelectedRisk] = useState<string>('medium');
  const [isLoading, setIsLoading] = useState(true);
  const [mapCenter, setMapCenter] = useState<[number, number]>([28.7041, 77.1025]);
  const [mapZoom, setMapZoom] = useState(12);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      
      // Fetch red zones
      const zones = await api.getRedZones({
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        min_risk: selectedRisk
      });
      setRedZones(zones);
      
      // Fetch heatmap data
      const heatmap = await api.getHeatmapData({
        category: selectedCategory === 'all' ? undefined : selectedCategory,
        days: 30
      });
      setHeatmapData(heatmap);
      
    } catch (error) {
      console.error('Failed to fetch red zone data:', error);
      toast.error('Failed to fetch red zone data');
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, selectedRisk]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getCategoryIcon = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'electricity':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'water':
        return <Droplets className="w-4 h-4 text-blue-500" />;
      case 'roads':
        return <div className="w-4 h-4 bg-gray-500 rounded-sm" />;
      case 'sanitation':
        return <Trash2 className="w-4 h-4 text-green-500" />;
      default:
        return <AlertTriangle className="w-4 h-4" />;
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return {
          fill: '#ef4444',
          stroke: '#dc2626',
          bg: 'bg-red-500/20 text-red-400 border-red-500/50'
        };
      case 'high':
        return {
          fill: '#f97316',
          stroke: '#ea580c',
          bg: 'bg-orange-500/20 text-orange-400 border-orange-500/50'
        };
      case 'medium':
        return {
          fill: '#eab308',
          stroke: '#ca8a04',
          bg: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50'
        };
      default:
        return {
          fill: '#22c55e',
          stroke: '#16a34a',
          bg: 'bg-green-500/20 text-green-400 border-green-500/50'
        };
    }
  };

  const getHeatmapColor = (intensity: number) => {
    // Return color based on intensity (0-1)
    if (intensity >= 0.8) return '#ef4444';
    if (intensity >= 0.6) return '#f97316';
    if (intensity >= 0.4) return '#eab308';
    if (intensity >= 0.2) return '#84cc16';
    return '#22c55e';
  };

  const criticalCount = redZones.filter(z => z.risk_level === 'critical').length;
  const highCount = redZones.filter(z => z.risk_level === 'high').length;
  const mediumCount = redZones.filter(z => z.risk_level === 'medium').length;

  return (
    <div className="space-y-4">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Critical Zones</p>
                <p className="text-2xl font-bold text-red-400">{criticalCount}</p>
              </div>
              <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">High Risk</p>
                <p className="text-2xl font-bold text-orange-400">{highCount}</p>
              </div>
              <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-orange-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Medium Risk</p>
                <p className="text-2xl font-bold text-yellow-400">{mediumCount}</p>
              </div>
              <div className="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <Info className="w-5 h-5 text-yellow-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Zones</p>
                <p className="text-2xl font-bold text-white">{redZones.length}</p>
              </div>
              <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center">
                <MapPin className="w-5 h-5 text-slate-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-sm text-slate-200"
              >
                <option value="all">All Categories</option>
                <option value="electricity">Electricity</option>
                <option value="water">Water</option>
                <option value="roads">Roads</option>
                <option value="sanitation">Sanitation</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-slate-400" />
              <select
                value={selectedRisk}
                onChange={(e) => setSelectedRisk(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-sm text-slate-200"
              >
                <option value="low">All Risk Levels</option>
                <option value="medium">Medium+ Risk</option>
                <option value="high">High+ Risk</option>
                <option value="critical">Critical Only</option>
              </select>
            </div>

            <div className="flex-1"></div>

            <Button
              variant="outline"
              size="sm"
              onClick={fetchData}
              disabled={isLoading}
              className="border-slate-700"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Map and List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Map */}
        <Card className="bg-slate-900 border-slate-800 lg:col-span-2 overflow-hidden">
          <div className="h-[500px] relative">
            <MapContainer
              center={mapCenter}
              zoom={mapZoom}
              style={{ height: '100%', width: '100%' }}
            >
              <MapController center={mapCenter} zoom={mapZoom} />
              
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              {/* Heatmap circles */}
              {heatmapData.map((point, index) => (
                <Circle
                  key={`heat-${index}`}
                  center={[point.latitude, point.longitude]}
                  radius={150}
                  pathOptions={{
                    fillColor: getHeatmapColor(point.intensity),
                    fillOpacity: point.intensity * 0.5,
                    color: getHeatmapColor(point.intensity),
                    weight: 1,
                  }}
                />
              ))}
              
              {/* Red zone markers */}
              {redZones.map((zone) => {
                const colors = getRiskColor(zone.risk_level);
                return (
                  <Circle
                    key={zone.id}
                    center={[zone.latitude, zone.longitude]}
                    radius={zone.radius_meters}
                    pathOptions={{
                      fillColor: colors.fill,
                      fillOpacity: 0.3,
                      color: colors.stroke,
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <div className="p-2 min-w-[250px]">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getCategoryIcon(zone.category)}
                            <span className="font-semibold capitalize">{zone.category}</span>
                          </div>
                          <Badge 
                            variant="outline" 
                            className={colors.bg}
                          >
                            {zone.risk_level}
                          </Badge>
                        </div>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-500">Failures (30d):</span>
                            <span className="font-medium">{zone.failure_count_30d}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500">Failures (90d):</span>
                            <span className="font-medium">{zone.failure_count_90d}</span>
                          </div>
                          
                          {zone.predicted_failure_at && (
                            <div className="flex justify-between text-red-600 font-bold bg-red-50 p-1 rounded">
                              <span>Predicted Failure:</span>
                              <span>{format(new Date(zone.predicted_failure_at), 'MMM dd, yyyy')}</span>
                            </div>
                          )}
                          
                          {zone.proactive_maintenance_deadline && (
                            <div className="flex justify-between text-orange-600 font-bold bg-orange-50 p-1 rounded border border-orange-200">
                              <span>Maintenance By:</span>
                              <span>{format(new Date(zone.proactive_maintenance_deadline), 'MMM dd, yyyy')}</span>
                            </div>
                          )}
                          
                          {zone.asset_type && (
                            <div className="flex justify-between">
                              <span className="text-slate-500">Asset Type:</span>
                              <span className="font-medium">{zone.asset_type}</span>
                            </div>
                          )}
                          
                          {zone.improvement_suggestion ? (
                            <div className="mt-3 p-2 bg-blue-50 border border-blue-100 rounded text-xs">
                              <p className="font-bold text-blue-700 mb-1 flex items-center gap-1">
                                <Zap className="w-3 h-3" /> Proactive Suggestion:
                              </p>
                              <p className="text-blue-600 italic">{zone.improvement_suggestion}</p>
                            </div>
                          ) : zone.recommended_action && (
                            <div className="mt-3 p-2 bg-slate-100 rounded text-xs">
                              <p className="font-medium text-slate-700 mb-1">Recommended Action:</p>
                              <p className="text-slate-600">{zone.recommended_action}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </Popup>
                  </Circle>
                );
              })}
            </MapContainer>
            
            {isLoading && (
              <div className="absolute inset-0 bg-slate-900/50 flex items-center justify-center">
                <div className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-lg">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Loading heatmap...</span>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Red Zone List */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-lg text-slate-200">Red Zone Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {redZones.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No red zones found</p>
                  <p className="text-sm">Great! Infrastructure is stable.</p>
                </div>
              ) : (
                redZones.map((zone) => {
                  const colors = getRiskColor(zone.risk_level);
                  return (
                    <div 
                      key={zone.id}
                      className="p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
                      onClick={() => {
                        setMapCenter([zone.latitude, zone.longitude]);
                        setMapZoom(15);
                      }}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(zone.category)}
                          <span className="font-medium text-sm capitalize">{zone.category}</span>
                        </div>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${colors.bg}`}
                        >
                          {zone.risk_level}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                        <span>30d: {zone.failure_count_30d} failures</span>
                        <span>90d: {zone.failure_count_90d} failures</span>
                      </div>
                      
                      {zone.proactive_maintenance_deadline && (
                        <div className="flex items-center gap-1 text-[10px] font-bold text-orange-500 mt-1">
                          <AlertTriangle className="w-3 h-3" />
                          <span>MAINTENANCE DUE: {format(new Date(zone.proactive_maintenance_deadline), 'MMM dd')}</span>
                        </div>
                      )}
                      
                      {zone.improvement_suggestion ? (
                        <p className="text-xs text-slate-300 line-clamp-2 mt-1">
                          {zone.improvement_suggestion}
                        </p>
                      ) : zone.recommended_action && (
                        <p className="text-xs text-slate-300 line-clamp-2 mt-1">
                          {zone.recommended_action}
                        </p>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Legend */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-slate-400">Heatmap Legend</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-500"></div>
              <span className="text-sm text-slate-300">Critical (80-100%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-orange-500"></div>
              <span className="text-sm text-slate-300">High (60-80%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-yellow-500"></div>
              <span className="text-sm text-slate-300">Medium (40-60%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-lime-500"></div>
              <span className="text-sm text-slate-300">Low (20-40%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-500"></div>
              <span className="text-sm text-slate-300">Minimal (0-20%)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
