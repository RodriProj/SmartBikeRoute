import * as ExpoLocation from 'expo-location';
import { Navigation, Play, Target, X } from 'lucide-react-native';
import React, { useEffect, useRef, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Keyboard,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import MapView, { MapPressEvent, Marker, Polyline } from 'react-native-maps';
import RouteConfigModal from './RouteConfigModal';
import {
    INITIAL_FORM,
    INITIAL_REGION,
    generatePersonalizedRoute,
    normalizeRouteCoordinates,
    reverseGeocodeCoords,
    searchLocation,
} from './api';
import { BackendRouteResponse, Coords, LocationSearchResult, ProfileType, RouteFormState, RouteSummary, SelectingMode } from './types';

const PROFILE_CONFIG: Record<ProfileType, { label: string; color: string; bg: string }> = {
  lazer:      { label: 'Lazer',      color: '#2ECC71', bg: '#2ECC7118' },
  exercicio:  { label: 'Exercício',  color: '#F39C12', bg: '#F39C1218' },
  competicao: { label: 'Competição', color: '#E74C3C', bg: '#E74C3C18' },
};

export default function RideScreen() {
  const mapRef = useRef<MapView>(null);

  const [configVisible, setConfigVisible] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(true);
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [loadingCurrentLocation, setLoadingCurrentLocation] = useState(false);
  const [selectingMode, setSelectingMode] = useState<SelectingMode>(null);

  const [startPoint, setStartPoint] = useState<Coords | null>({ latitude: 41.2952, longitude: -7.7460 });
  const [endPoint, setEndPoint]     = useState<Coords | null>(null);
  const [startAddress, setStartAddress] = useState('');
  const [endAddress, setEndAddress]     = useState('');

  const [startSuggestions, setStartSuggestions] = useState<LocationSearchResult[]>([]);
  const [endSuggestions, setEndSuggestions]     = useState<LocationSearchResult[]>([]);
  const [loadingStartSugg, setLoadingStartSugg] = useState(false);
  const [loadingEndSugg, setLoadingEndSugg]     = useState(false);

  const [userLocation, setUserLocation] = useState<Coords | null>(null);
  const [routeCoordinates, setRouteCoordinates] = useState<Coords[]>([]);
  const [routeSummary, setRouteSummary]         = useState<RouteSummary | null>(null);
  const [routeForm, setRouteForm]               = useState<RouteFormState>(INITIAL_FORM);

  const profile = PROFILE_CONFIG[routeForm.profile_type];

  // ── Obter localização do utilizador ao arrancar ────────────────────────────
  useEffect(() => {
    (async () => {
      try {
        const { status } = await ExpoLocation.requestForegroundPermissionsAsync();
        if (status !== 'granted') return;
        const pos = await ExpoLocation.getCurrentPositionAsync({});
        setUserLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
      } catch {}
    })();
  }, []);

  // ── Debounced autocomplete ─────────────────────────────────────────────────
  useEffect(() => {
    if (startAddress.trim().length < 2) { setStartSuggestions([]); return; }
    const timer = setTimeout(async () => {
      try {
        setLoadingStartSugg(true);
        const results = await searchLocation(startAddress, userLocation ?? undefined);
        setStartSuggestions(results.slice(0, 5));
      } catch {
        setStartSuggestions([]);
      } finally {
        setLoadingStartSugg(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [startAddress, userLocation]);

  useEffect(() => {
    if (endAddress.trim().length < 2 || routeForm.loop) { setEndSuggestions([]); return; }
    const timer = setTimeout(async () => {
      try {
        setLoadingEndSugg(true);
        const results = await searchLocation(endAddress, userLocation ?? undefined);
        setEndSuggestions(results.slice(0, 5));
      } catch {
        setEndSuggestions([]);
      } finally {
        setLoadingEndSugg(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [endAddress, routeForm.loop, userLocation]);

  const pickSuggestion = (item: LocationSearchResult, mode: 'start' | 'end') => {
    const coords = { latitude: item.latitude, longitude: item.longitude };
    if (mode === 'start') {
      setStartPoint(coords);
      setStartAddress(item.name);
      setStartSuggestions([]);
    } else {
      setEndPoint(coords);
      setEndAddress(item.name);
      setEndSuggestions([]);
    }
    Keyboard.dismiss();
    mapRef.current?.animateToRegion({ ...coords, latitudeDelta: 0.02, longitudeDelta: 0.02 });
  };

  // ── Profile switch ─────────────────────────────────────────────────────────
  const setProfile = (p: ProfileType) => {
    setRouteForm((prev) => {
      const next = { ...prev, profile_type: p };
      if (p === 'lazer')      { next.training_goal = null;            next.intensity_preference = 'media'; next.route_fluency = 'media'; }
      if (p === 'exercicio')  { next.training_goal = 'queimar_gordura'; next.intensity_preference = 'media'; next.route_fluency = 'media'; }
      if (p === 'competicao') { next.training_goal = 'velocidade';    next.intensity_preference = 'alta';  next.route_fluency = 'alta'; }
      return next;
    });
    setRouteCoordinates([]);
    setRouteSummary(null);
  };

  // ── Map interaction ────────────────────────────────────────────────────────
  const formatCoords = (c: Coords) => `${c.latitude.toFixed(5)}, ${c.longitude.toFixed(5)}`;

  const updatePointFromMap = async (coords: Coords, mode: 'start' | 'end') => {
    if (mode === 'start') { setStartPoint(coords); setStartAddress(formatCoords(coords)); setStartSuggestions([]); }
    else                  { setEndPoint(coords);   setEndAddress(formatCoords(coords));   setEndSuggestions([]); }
    try {
      const human = await reverseGeocodeCoords(coords);
      if (human) {
        if (mode === 'start') setStartAddress(human);
        else setEndAddress(human);
      }
    } catch {}
  };

  const handleMapPress = async (event: MapPressEvent) => {
    if (!selectingMode) return;
    await updatePointFromMap(event.nativeEvent.coordinate, selectingMode);
    setSelectingMode(null);
  };

  const useCurrentLocation = async () => {
    try {
      setLoadingCurrentLocation(true);
      const { status } = await ExpoLocation.requestForegroundPermissionsAsync();
      if (status !== 'granted') { Alert.alert('Permissão necessária', 'Ativa o acesso à localização nas definições.'); return; }
      const current = await ExpoLocation.getCurrentPositionAsync({});
      const coords  = { latitude: current.coords.latitude, longitude: current.coords.longitude };
      await updatePointFromMap(coords, 'start');
      mapRef.current?.animateToRegion({ ...coords, latitudeDelta: 0.01, longitudeDelta: 0.01 });
    } catch {
      Alert.alert('Erro', 'Não foi possível obter a localização atual.');
    } finally {
      setLoadingCurrentLocation(false);
    }
  };

  // ── Route generation ───────────────────────────────────────────────────────
  const clearRoute = () => { setRouteCoordinates([]); setRouteSummary(null); };

  const generateRoute = async () => {
    const finalEnd = routeForm.loop ? startPoint : endPoint;
    if (!startPoint) { Alert.alert('Ponto inicial em falta', 'Seleciona o ponto de início.'); return; }
    if (!finalEnd)   { Alert.alert('Ponto final em falta', 'Seleciona o destino ou ativa o loop.'); return; }
    try {
      setLoadingRoute(true);
      const result: BackendRouteResponse = await generatePersonalizedRoute({
        ...routeForm,
        startLat: startPoint.latitude, startLon: startPoint.longitude,
        endLat: finalEnd.latitude,     endLon: finalEnd.longitude,
      });
      const coords = normalizeRouteCoordinates(result);
      if (coords.length === 0) {
        Alert.alert('Sem rota disponível', 'Não foi possível encontrar uma rota entre estes pontos. Tenta pontos mais próximos ou um perfil diferente.');
        return;
      }
      setRouteCoordinates(coords);
      setRouteSummary(result.route_summary ?? null);
      setConfigVisible(false);
      mapRef.current?.fitToCoordinates(coords, { edgePadding: { top: 200, right: 40, bottom: 200, left: 40 }, animated: true });
    } catch (error: any) {
      Alert.alert('Erro', error?.message ?? 'Não foi possível gerar a rota.');
    } finally {
      setLoadingRoute(false);
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  const showStartSugg = startSuggestions.length > 0;
  const showEndSugg   = endSuggestions.length > 0;

  return (
    <View style={styles.container}>
      <MapView ref={mapRef} style={styles.map} initialRegion={INITIAL_REGION} onPress={handleMapPress}>
        {startPoint && <Marker coordinate={startPoint} title="Início" pinColor="green" />}
        {!routeForm.loop && endPoint && <Marker coordinate={endPoint} title="Fim" pinColor="red" />}
        {routeCoordinates.length > 0 && (
          <Polyline coordinates={routeCoordinates} strokeColor={profile.color} strokeWidth={6} />
        )}
      </MapView>

      {/* Selecting mode banner */}
      {selectingMode && (
        <View style={styles.selectingBanner}>
          <Target size={14} color="#1EB1FC" />
          <Text style={styles.selectingText}>
            Toca no mapa para definir o {selectingMode === 'start' ? 'início' : 'destino'}
          </Text>
          <TouchableOpacity onPress={() => setSelectingMode(null)}>
            <X size={15} color="#8b949e" />
          </TouchableOpacity>
        </View>
      )}

      {/* Route input panel */}
      <View style={styles.routePanel}>

        {/* Start input row */}
        <View style={styles.pointRow}>
          <View style={styles.dotCol}><View style={[styles.dot, styles.dotStart]} /></View>
          <TextInput
            style={[styles.pointInput, selectingMode === 'start' && styles.pointInputActive]}
            placeholder="Ponto de início"
            placeholderTextColor="#9ca3af"
            value={startAddress}
            onChangeText={(t) => { setStartAddress(t); }}
            returnKeyType="search"
            onFocus={() => setSelectingMode(null)}
          />
          {loadingStartSugg || loadingCurrentLocation ? (
            <ActivityIndicator size="small" color="#1EB1FC" style={styles.rowAction} />
          ) : (
            <View style={styles.rowActions}>
              <TouchableOpacity onPress={() => { setStartSuggestions([]); setSelectingMode('start'); }} style={styles.rowAction}>
                <Target size={16} color={selectingMode === 'start' ? '#1EB1FC' : '#9ca3af'} />
              </TouchableOpacity>
              <TouchableOpacity onPress={useCurrentLocation} style={styles.rowAction}>
                <Navigation size={16} color="#9ca3af" />
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Start suggestions */}
        {showStartSugg && (
          <View style={styles.suggList}>
            {startSuggestions.map((item, i) => (
              <TouchableOpacity
                key={i}
                style={[styles.suggItem, i < startSuggestions.length - 1 && styles.suggItemBorder]}
                onPress={() => pickSuggestion(item, 'start')}
              >
                <Text style={styles.suggName} numberOfLines={1}>{item.name}</Text>
                {item.address !== item.name && (
                  <Text style={styles.suggAddr} numberOfLines={1}>{item.address}</Text>
                )}
              </TouchableOpacity>
            ))}
          </View>
        )}

        <View style={styles.connector}><View style={styles.connectorLine} /></View>

        {/* End input row */}
        <View style={styles.pointRow}>
          <View style={styles.dotCol}><View style={[styles.dot, styles.dotEnd]} /></View>
          <TextInput
            style={[
              styles.pointInput,
              selectingMode === 'end' && styles.pointInputActive,
              routeForm.loop && styles.pointInputDisabled,
            ]}
            placeholder={routeForm.loop ? 'Loop — regresso ao início' : 'Destino'}
            placeholderTextColor="#9ca3af"
            value={routeForm.loop ? '' : endAddress}
            onChangeText={(t) => { setEndAddress(t); }}
            returnKeyType="search"
            editable={!routeForm.loop}
            onFocus={() => setSelectingMode(null)}
          />
          {loadingEndSugg ? (
            <ActivityIndicator size="small" color="#1EB1FC" style={styles.rowAction} />
          ) : !routeForm.loop ? (
            <TouchableOpacity onPress={() => { setEndSuggestions([]); setSelectingMode('end'); }} style={styles.rowAction}>
              <Target size={16} color={selectingMode === 'end' ? '#1EB1FC' : '#9ca3af'} />
            </TouchableOpacity>
          ) : null}
        </View>

        {/* End suggestions */}
        {showEndSugg && (
          <View style={styles.suggList}>
            {endSuggestions.map((item, i) => (
              <TouchableOpacity
                key={i}
                style={[styles.suggItem, i < endSuggestions.length - 1 && styles.suggItemBorder]}
                onPress={() => pickSuggestion(item, 'end')}
              >
                <Text style={styles.suggName} numberOfLines={1}>{item.name}</Text>
                {item.address !== item.name && (
                  <Text style={styles.suggAddr} numberOfLines={1}>{item.address}</Text>
                )}
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Profile tabs */}
        <View style={styles.profileTabs}>
          {(Object.keys(PROFILE_CONFIG) as ProfileType[]).map((p) => {
            const cfg    = PROFILE_CONFIG[p];
            const active = routeForm.profile_type === p;
            return (
              <TouchableOpacity
                key={p}
                onPress={() => setProfile(p)}
                style={[styles.profileTab, active && { backgroundColor: cfg.bg, borderColor: cfg.color }]}
              >
                <Text style={[styles.profileTabText, active && { color: cfg.color }]}>{cfg.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Route summary */}
      {routeSummary && (
        <View style={styles.summaryCard}>
          <View style={styles.summaryHeader}>
            <View style={[styles.profileBadge, { backgroundColor: profile.bg }]}>
              <View style={[styles.profileDot, { backgroundColor: profile.color }]} />
              <Text style={[styles.profileBadgeText, { color: profile.color }]}>{profile.label}</Text>
            </View>
            <TouchableOpacity onPress={clearRoute} style={styles.clearBtn}>
              <X size={15} color="#6b7280" />
            </TouchableOpacity>
          </View>
          <View style={styles.summaryStats}>
            <View style={styles.statItem}>
              <Text style={styles.statVal}>{routeSummary.distance_km ?? '—'}</Text>
              <Text style={styles.statLabel}>km</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statVal}>{routeSummary.estimated_time_min ?? '—'}</Text>
              <Text style={styles.statLabel}>min</Text>
            </View>
            {routeSummary.distance_difference_km != null && (
              <>
                <View style={styles.statDivider} />
                <View style={styles.statItem}>
                  <Text style={[styles.statVal, { color: Math.abs(routeSummary.distance_difference_km) < 2 ? '#2ECC71' : '#F39C12' }]}>
                    {routeSummary.distance_difference_km > 0 ? '+' : ''}{routeSummary.distance_difference_km}
                  </Text>
                  <Text style={styles.statLabel}>dif. km</Text>
                </View>
              </>
            )}
          </View>
        </View>
      )}

      {/* Configure button */}
      <TouchableOpacity
        style={[styles.playButton, { backgroundColor: profile.color }]}
        onPress={() => { Keyboard.dismiss(); setStartSuggestions([]); setEndSuggestions([]); setConfigVisible(true); }}
      >
        <Play size={18} color="#FFF" />
        <Text style={styles.playButtonText}>Configurar percurso</Text>
      </TouchableOpacity>

      <RouteConfigModal
        visible={configVisible}
        loading={loadingRoute}
        showAdvanced={showAdvanced}
        setShowAdvanced={setShowAdvanced}
        form={routeForm}
        setForm={setRouteForm}
        onClose={() => setConfigVisible(false)}
        onSubmit={generateRoute}
        onClearRoute={clearRoute}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { ...StyleSheet.absoluteFillObject },

  selectingBanner: {
    position: 'absolute', top: 10, alignSelf: 'center',
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#161b22ee', borderRadius: 20,
    paddingHorizontal: 14, paddingVertical: 8,
    borderWidth: 1, borderColor: '#1EB1FC44',
  },
  selectingText: { color: '#e6edf3', fontSize: 12, flex: 1 },

  routePanel: {
    position: 'absolute', top: 46, left: 14, right: 14,
    backgroundColor: '#fffffff6', borderRadius: 18,
    paddingHorizontal: 12, paddingTop: 10, paddingBottom: 8,
    elevation: 6,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.12, shadowRadius: 8,
  },

  pointRow:   { flexDirection: 'row', alignItems: 'center', gap: 8 },
  dotCol:     { width: 20, alignItems: 'center' },
  dot:        { width: 11, height: 11, borderRadius: 6, borderWidth: 2 },
  dotStart:   { backgroundColor: '#2ECC71', borderColor: '#27ae60' },
  dotEnd:     { backgroundColor: '#E74C3C', borderColor: '#c0392b' },
  connector:  { paddingLeft: 14, height: 10, justifyContent: 'center' },
  connectorLine: { width: 2, height: 10, backgroundColor: '#e5e7eb', marginLeft: -1 },

  pointInput:         { flex: 1, fontSize: 13, color: '#111827', paddingVertical: 6, paddingHorizontal: 2 },
  pointInputActive:   { color: '#1EB1FC' },
  pointInputDisabled: { color: '#9ca3af' },
  rowActions: { flexDirection: 'row', gap: 2 },
  rowAction:  { padding: 6 },

  // Suggestions
  suggList: {
    marginLeft: 28, marginTop: 2, marginBottom: 2,
    backgroundColor: '#fff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    overflow: 'hidden',
  },
  suggItem: { paddingHorizontal: 12, paddingVertical: 9 },
  suggItemBorder: { borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  suggName: { fontSize: 13, fontWeight: '600', color: '#111827' },
  suggAddr: { fontSize: 11, color: '#9ca3af', marginTop: 1 },

  // Profile tabs
  profileTabs: {
    flexDirection: 'row', gap: 6, marginTop: 10,
    paddingTop: 10, borderTopWidth: 1, borderTopColor: '#f3f4f6',
  },
  profileTab: {
    flex: 1, paddingVertical: 7, borderRadius: 10,
    borderWidth: 1.5, borderColor: '#e5e7eb',
    backgroundColor: '#f9fafb', alignItems: 'center',
  },
  profileTabText: { fontSize: 11, fontWeight: '700', color: '#9ca3af' },

  // Summary
  summaryCard: {
    position: 'absolute', left: 14, right: 14, bottom: 100,
    backgroundColor: '#fffffff6', borderRadius: 16,
    paddingHorizontal: 14, paddingVertical: 10, elevation: 5,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.10, shadowRadius: 6,
  },
  summaryHeader:   { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  profileBadge:    { flexDirection: 'row', alignItems: 'center', gap: 5, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  profileDot:      { width: 7, height: 7, borderRadius: 4 },
  profileBadgeText:{ fontSize: 12, fontWeight: '700' },
  clearBtn:        { padding: 4 },
  summaryStats:    { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' },
  statItem:        { alignItems: 'center', flex: 1 },
  statVal:         { fontSize: 20, fontWeight: '800', color: '#111827' },
  statLabel:       { fontSize: 11, color: '#9ca3af', marginTop: 1 },
  statDivider:     { width: 1, height: 30, backgroundColor: '#e5e7eb' },

  // Play button
  playButton: {
    position: 'absolute', bottom: 26, alignSelf: 'center',
    borderRadius: 999, paddingHorizontal: 22, paddingVertical: 14,
    flexDirection: 'row', alignItems: 'center', gap: 8, elevation: 6,
  },
  playButtonText: { color: '#FFF', fontWeight: '800', fontSize: 14 },
});
