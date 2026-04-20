import * as ExpoLocation from 'expo-location';
import {
    BackendRouteResponse,
    CompetitionGoal,
    Coords,
    ExerciseGoal,
    LocationSearchResult,
    RouteFormState,
} from './types';

export const API_BASE = 'http://192.168.1.128:8000';

export const INITIAL_REGION = {
  latitude: 41.2952,
  longitude: -7.7460,
  latitudeDelta: 0.02,
  longitudeDelta: 0.02,
};

export const INITIAL_FORM: RouteFormState = {
  profile_type: 'lazer',
  target_distance_km: 12,
  loop: false,
  elevation_preference: 'media',
  scenic_preference: 'media',
  traffic_avoidance: 'media',
  environment_preference: 'mista',
  surface_preference: 'indiferente',
  difficulty_level: 'facil',
  points_of_interest_preference: 'media',
  green_area_preference: 'media',
  intensity_preference: 'media',
  route_fluency: 'media',
  training_goal: null,
};

export const EXERCISE_GOALS: ExerciseGoal[] = [
  'queimar_gordura',
  'ganhar_resistencia',
  'trabalhar_musculo',
  'recuperacao_ativa',
  'treino_misto',
];

export const COMPETITION_GOALS: CompetitionGoal[] = [
  'velocidade',
  'ritmo_constante',
  'subida',
  'resistencia_competitiva',
  'simulacao_prova',
];

export async function generatePersonalizedRoute(
  payload: {
    startLat: number;
    startLon: number;
    endLat: number;
    endLon: number;
  } & RouteFormState,
): Promise<BackendRouteResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);

  try {
    const response = await fetch(`${API_BASE}/routes/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `Erro ${response.status}`);
    }

    return response.json();
  } catch (err: any) {
    if (err?.name === 'AbortError') {
      throw new Error('O pedido demorou demasiado. Verifica a ligação ao servidor.');
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export async function searchLocation(
  query: string,
  userLocation?: { latitude: number; longitude: number },
): Promise<LocationSearchResult[]> {
  const trimmed = query.trim();
  if (!trimmed) return [];

  try {
    const backendResponse = await fetch(
      `${API_BASE}/locations/search?q=${encodeURIComponent(trimmed)}`,
      {
        headers: {
          Accept: 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
      },
    );

    if (backendResponse.ok) {
      const data = await backendResponse.json();

      if (Array.isArray(data)) {
        return data.map((item: any) => ({
          name: item.name ?? item.address ?? trimmed,
          address: item.address ?? item.name ?? trimmed,
          latitude: Number(item.latitude),
          longitude: Number(item.longitude),
        }));
      }
    }
  } catch {
    // fallback
  }

  // Se temos localização do utilizador, usamos como centro de bias
  // bounded=0 prioriza mas não exclui resultados fora da área
  const lat = userLocation?.latitude ?? INITIAL_REGION.latitude;
  const lon = userLocation?.longitude ?? INITIAL_REGION.longitude;
  const delta = 0.5; // ~50km de raio
  const viewbox = `${lon - delta},${lat + delta},${lon + delta},${lat - delta}`;

  const response = await fetch(
    `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&countrycodes=pt&viewbox=${viewbox}&bounded=0&q=${encodeURIComponent(trimmed)}`,
    {
      headers: {
        Accept: 'application/json',
      },
    },
  );

  if (!response.ok) {
    throw new Error('Falha na pesquisa de localização.');
  }

  const data = await response.json();

  if (!Array.isArray(data)) return [];

  return data.map((item: any) => ({
    name: item.display_name ?? trimmed,
    address: item.display_name ?? trimmed,
    latitude: Number(item.lat),
    longitude: Number(item.lon),
  }));
}

export async function reverseGeocodeCoords(coords: Coords): Promise<string> {
  try {
    const backendResponse = await fetch(
      `${API_BASE}/locations/reverse?lat=${coords.latitude}&lon=${coords.longitude}`,
      {
        headers: {
          Accept: 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
      },
    );

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      if (data?.address) return data.address;
      if (data?.name) return data.name;
    }
  } catch {
    // fallback
  }

  try {
    const reverse = await ExpoLocation.reverseGeocodeAsync(coords);
    const item = reverse?.[0];

    if (!item) {
      return `${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`;
    }

    return [item.name, item.street, item.city, item.region]
      .filter(Boolean)
      .join(', ');
  } catch {
    return `${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`;
  }
}

export function normalizeRouteCoordinates(result: BackendRouteResponse): Coords[] {
  const geometry = result?.route?.features?.[0]?.geometry;

  if (!geometry) {
    return [];
  }

  if (geometry.type === 'LineString') {
    return geometry.coordinates.map(([lon, lat]) => ({
      latitude: lat,
      longitude: lon,
    }));
  }

  if (geometry.type === 'MultiLineString') {
    return geometry.coordinates.flatMap((line) =>
      line.map(([lon, lat]) => ({
        latitude: lat,
        longitude: lon,
      })),
    );
  }

  if (geometry.type === 'GeometryCollection') {
    return geometry.geometries.flatMap((geom: any) => {
      if (geom.type === 'LineString') {
        return geom.coordinates.map(([lon, lat]: number[]) => ({ latitude: lat, longitude: lon }));
      }
      if (geom.type === 'MultiLineString') {
        return geom.coordinates.flatMap((line: number[][]) =>
          line.map(([lon, lat]) => ({ latitude: lat, longitude: lon })),
        );
      }
      return [];
    });
  }

  return [];
}