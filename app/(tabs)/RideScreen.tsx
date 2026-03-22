import * as ExpoLocation from 'expo-location';
import { MapPin, Navigation, Play, Search, Target } from 'lucide-react-native';
import React, { useMemo, useRef, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
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
    searchLocation
} from './api';
import { BackendRouteResponse, Coords, RouteFormState, RouteSummary, SelectingMode } from './types';

export default function RideScreen() {
  const mapRef = useRef<MapView>(null);

  const [configVisible, setConfigVisible] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(true);

  const [loadingRoute, setLoadingRoute] = useState(false);
  const [loadingStartSearch, setLoadingStartSearch] = useState(false);
  const [loadingEndSearch, setLoadingEndSearch] = useState(false);
  const [loadingCurrentLocation, setLoadingCurrentLocation] = useState(false);

  const [selectingMode, setSelectingMode] = useState<SelectingMode>(null);

  const [startPoint, setStartPoint] = useState<Coords | null>({
    latitude: 41.2952,
    longitude: -7.7460,
  });
  const [endPoint, setEndPoint] = useState<Coords | null>(null);

  const [startAddress, setStartAddress] = useState('');
  const [endAddress, setEndAddress] = useState('');

  const [routeCoordinates, setRouteCoordinates] = useState<Coords[]>([]);
  const [routeSummary, setRouteSummary] = useState<RouteSummary | null>(null);

  const [routeForm, setRouteForm] = useState<RouteFormState>(INITIAL_FORM);

  const polylineColor = useMemo(() => {
    if (routeForm.profile_type === 'lazer') return '#2ECC71';
    if (routeForm.profile_type === 'exercicio') return '#F39C12';
    return '#E74C3C';
  }, [routeForm.profile_type]);

  const formatCoords = (coords: Coords | null) => {
    if (!coords) return '';
    return `${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`;
  };

  const updatePointFromMap = async (coords: Coords, mode: 'start' | 'end') => {
    if (mode === 'start') {
      setStartPoint(coords);
      if (!startAddress.trim()) setStartAddress(formatCoords(coords));
    } else {
      setEndPoint(coords);
      if (!endAddress.trim()) setEndAddress(formatCoords(coords));
    }

    try {
      const humanAddress = await reverseGeocodeCoords(coords);
      if (humanAddress) {
        if (mode === 'start') setStartAddress(humanAddress);
        else setEndAddress(humanAddress);
      }
    } catch {
      // fallback silencioso
    }
  };

  const handleMapPress = async (event: MapPressEvent) => {
    if (!selectingMode) return;
    const coords = event.nativeEvent.coordinate;
    await updatePointFromMap(coords, selectingMode);
    setSelectingMode(null);
  };

  const useCurrentLocation = async () => {
    try {
      setLoadingCurrentLocation(true);

      const { status } = await ExpoLocation.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissão necessária', 'Ativa o acesso à localização para usar o GPS.');
        return;
      }

      const current = await ExpoLocation.getCurrentPositionAsync({});
      const coords = {
        latitude: current.coords.latitude,
        longitude: current.coords.longitude,
      };

      await updatePointFromMap(coords, 'start');

      mapRef.current?.animateToRegion({
        ...coords,
        latitudeDelta: 0.01,
        longitudeDelta: 0.01,
      });
    } catch {
      Alert.alert('Erro', 'Não foi possível obter a localização atual.');
    } finally {
      setLoadingCurrentLocation(false);
    }
  };

  const searchAddress = async (
    query: string,
    mode: 'start' | 'end',
    setLoading: React.Dispatch<React.SetStateAction<boolean>>,
  ) => {
    if (!query.trim()) {
      Alert.alert('Morada vazia', 'Introduz uma morada ou local.');
      return;
    }

    try {
      setLoading(true);
      const results = await searchLocation(query);

      if (!results.length) {
        Alert.alert('Sem resultados', 'Não foi encontrado nenhum local com essa pesquisa.');
        return;
      }

      const first = results[0];
      const coords = {
        latitude: first.latitude,
        longitude: first.longitude,
      };

      if (mode === 'start') {
        setStartPoint(coords);
        setStartAddress(first.address);
      } else {
        setEndPoint(coords);
        setEndAddress(first.address);
      }

      mapRef.current?.animateToRegion({
        ...coords,
        latitudeDelta: 0.02,
        longitudeDelta: 0.02,
      });
    } catch {
      Alert.alert('Erro', 'Não foi possível pesquisar a morada.');
    } finally {
      setLoading(false);
    }
  };

  const clearRoute = () => {
    setRouteCoordinates([]);
    setRouteSummary(null);
  };

  function buildRoutePayload(
  startPoint: Coords,
  endPoint: Coords,
  form: RouteFormState,
): RouteFormState & {
  startLat: number;
  startLon: number;
  endLat: number;
  endLon: number;
} {
  return {
    ...form,
    startLat: startPoint.latitude,
    startLon: startPoint.longitude,
    endLat: endPoint.latitude,
    endLon: endPoint.longitude,
  };
}
const generateRoute = async () => {
  const finalEndPoint = routeForm.loop ? startPoint : endPoint;

  if (!startPoint) {
    Alert.alert('Ponto inicial em falta', 'Seleciona o ponto de início.');
    return;
  }

  if (!finalEndPoint) {
    Alert.alert('Ponto final em falta', 'Seleciona o ponto de fim ou ativa o loop.');
    return;
  }

  try {
    setLoadingRoute(true);

    const payload = buildRoutePayload(startPoint, finalEndPoint, routeForm);

    const result: BackendRouteResponse = await generatePersonalizedRoute(payload);
    const coords = normalizeRouteCoordinates(result);

    setRouteCoordinates(coords);
    setRouteSummary(result.route_summary ?? null);
    setConfigVisible(false);

    if (coords.length > 0) {
      mapRef.current?.fitToCoordinates(coords, {
        edgePadding: { top: 120, right: 40, bottom: 120, left: 40 },
        animated: true,
      });
    }
  } catch (error) {
    console.error('Erro ao gerar rota:', error);
    Alert.alert('Erro', 'Não foi possível gerar a rota com as opções atuais.');
  } finally {
    setLoadingRoute(false);
  }
};

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        initialRegion={INITIAL_REGION}
        onPress={handleMapPress}
      >
        {startPoint && <Marker coordinate={startPoint} title="Início" pinColor="green" />}
        {!routeForm.loop && endPoint && <Marker coordinate={endPoint} title="Fim" pinColor="red" />}
        {routeCoordinates.length > 0 && (
          <Polyline coordinates={routeCoordinates} strokeColor={polylineColor} strokeWidth={6} />
        )}
      </MapView>

      <View style={styles.mapTopPanel}>
        <View style={[styles.locationCard, selectingMode === 'start' && styles.locationCardActive]}>
          <View style={styles.locationHeaderRow}>
            <View style={styles.locationTitleRow}>
              <MapPin size={18} color="#2ECC71" />
              <Text style={styles.locationTitle}>Início</Text>
            </View>

            <View style={styles.locationActionsRow}>
              <TouchableOpacity onPress={() => setSelectingMode('start')} style={styles.iconActionButton}>
                <Target size={18} color="#1EB1FC" />
              </TouchableOpacity>

              <TouchableOpacity onPress={useCurrentLocation} style={styles.iconActionButton}>
                {loadingCurrentLocation ? (
                  <ActivityIndicator size="small" color="#1EB1FC" />
                ) : (
                  <Navigation size={18} color="#1EB1FC" />
                )}
              </TouchableOpacity>
            </View>
          </View>

          <TextInput
            placeholder="Escrever morada ou local de início"
            value={startAddress}
            onChangeText={setStartAddress}
            style={styles.addressInput}
          />

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => searchAddress(startAddress, 'start', setLoadingStartSearch)}
          >
            {loadingStartSearch ? (
              <ActivityIndicator size="small" color="#1EB1FC" />
            ) : (
              <>
                <Search size={16} color="#1EB1FC" />
                <Text style={styles.secondaryButtonText}>Procurar início</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        <View style={[styles.locationCard, selectingMode === 'end' && styles.locationCardActive]}>
          <View style={styles.locationHeaderRow}>
            <View style={styles.locationTitleRow}>
              <MapPin size={18} color="#E74C3C" />
              <Text style={styles.locationTitle}>Fim</Text>
            </View>

            <TouchableOpacity onPress={() => setSelectingMode('end')} style={styles.iconActionButton}>
              <Target size={18} color="#1EB1FC" />
            </TouchableOpacity>
          </View>

          <TextInput
            placeholder="Escrever morada ou destino final"
            value={endAddress}
            onChangeText={setEndAddress}
            style={styles.addressInput}
            editable={!routeForm.loop}
          />

          <TouchableOpacity
            style={[styles.secondaryButton, routeForm.loop && styles.disabledButton]}
            disabled={routeForm.loop}
            onPress={() => searchAddress(endAddress, 'end', setLoadingEndSearch)}
          >
            {loadingEndSearch ? (
              <ActivityIndicator size="small" color="#1EB1FC" />
            ) : (
              <>
                <Search size={16} color="#1EB1FC" />
                <Text style={styles.secondaryButtonText}>Procurar fim</Text>
              </>
            )}
          </TouchableOpacity>

          {routeForm.loop && (
            <Text style={styles.helperText}>
              Loop ativo: a rota termina automaticamente no ponto de início.
            </Text>
          )}
        </View>
      </View>

      {routeSummary && (
        <View style={styles.routeSummaryCard}>
          <Text style={styles.routeSummaryTitle}>Resumo da rota</Text>
          <Text style={styles.routeSummaryText}>Distância: {routeSummary.distance_km ?? '-'} km</Text>
          <Text style={styles.routeSummaryText}>
            Tempo estimado: {routeSummary.estimated_time_min ?? '-'} min
          </Text>
          <Text style={styles.routeSummaryText}>
            Estratégia: {routeSummary.routing_strategy_used ?? '-'}
          </Text>
        </View>
      )}

      <TouchableOpacity style={styles.playButton} onPress={() => setConfigVisible(true)}>
        <Play size={22} color="#FFF" />
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
  container: {
    flex: 1,
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  mapTopPanel: {
    position: 'absolute',
    top: 46,
    left: 14,
    right: 14,
    gap: 10,
  },
  locationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 14,
    elevation: 4,
  },
  locationCardActive: {
    borderWidth: 2,
    borderColor: '#1EB1FC',
  },
  locationHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  locationTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  locationTitle: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },
  locationActionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconActionButton: {
    marginLeft: 10,
  },
  addressInput: {
    marginTop: 12,
    backgroundColor: '#EEF2F7',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: '#111827',
  },
  secondaryButton: {
    marginTop: 10,
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#EEF7FF',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  secondaryButtonText: {
    marginLeft: 8,
    color: '#1EB1FC',
    fontWeight: '700',
    fontSize: 13,
  },
  disabledButton: {
    opacity: 0.45,
  },
  helperText: {
    marginTop: 8,
    color: '#6B7280',
    fontSize: 12,
  },
  routeSummaryCard: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 120,
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    elevation: 4,
  },
  routeSummaryTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  routeSummaryText: {
    fontSize: 13,
    color: '#374151',
    marginBottom: 4,
  },
  playButton: {
    position: 'absolute',
    bottom: 26,
    alignSelf: 'center',
    backgroundColor: '#1EB1FC',
    borderRadius: 999,
    paddingHorizontal: 22,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 6,
  },
  playButtonText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
    marginLeft: 10,
  },
});