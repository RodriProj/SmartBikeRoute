export type TabKey = 'Home' | 'Pedalar' | 'Perfil';
export type SelectingMode = 'start' | 'end' | null;

export type ProfileType = 'lazer' | 'exercicio' | 'competicao';
export type PreferenceLevel = 'baixa' | 'media' | 'alta';
export type EnvironmentPreference = 'urbana' | 'rural' | 'mista';
export type SurfacePreference = 'asfalto' | 'asfalto_ecovia' | 'indiferente';
export type DifficultyLevel = 'muito_facil' | 'facil' | 'moderada';

export type ExerciseGoal =
  | 'queimar_gordura'
  | 'ganhar_resistencia'
  | 'trabalhar_musculo'
  | 'recuperacao_ativa'
  | 'treino_misto';

export type CompetitionGoal =
  | 'velocidade'
  | 'ritmo_constante'
  | 'subida'
  | 'resistencia_competitiva'
  | 'simulacao_prova';

export type TrainingGoal = ExerciseGoal | CompetitionGoal | null;

export interface Coords {
  latitude: number;
  longitude: number;
}

export interface RouteFormState {
  profile_type: ProfileType;
  target_distance_km: number;
  loop: boolean;
  elevation_preference: PreferenceLevel;
  scenic_preference: PreferenceLevel;
  traffic_avoidance: PreferenceLevel;
  environment_preference: EnvironmentPreference;
  surface_preference: SurfacePreference;
  difficulty_level: DifficultyLevel;
  points_of_interest_preference: PreferenceLevel;
  green_area_preference: PreferenceLevel;
  intensity_preference: PreferenceLevel;
  route_fluency: PreferenceLevel;
  training_goal: TrainingGoal;
}

export interface RouteSummary {
  distance_m?: number;
  distance_km?: number;
  estimated_time_min?: number;
  target_distance_km?: number | null;
  distance_difference_km?: number;
  routing_strategy_used?: string;
}

export interface RouteGeometryLineString {
  type: 'LineString';
  coordinates: [number, number][];
}

export interface RouteGeometryMultiLineString {
  type: 'MultiLineString';
  coordinates: [number, number][][];
}

export interface RouteGeometryCollection {
  type: 'GeometryCollection';
  geometries: Array<RouteGeometryLineString | RouteGeometryMultiLineString>;
}

export type RouteGeometry = RouteGeometryLineString | RouteGeometryMultiLineString | RouteGeometryCollection;

export interface BackendRouteResponse {
  profile_type: ProfileType;
  session_profile?: Record<string, unknown>;
  preferences?: Record<string, unknown>;
  route_summary?: RouteSummary;
  route?: {
    type: string;
    features: Array<{
      type: string;
      properties: Record<string, unknown>;
      geometry: RouteGeometry;
    }>;
  };
}

export interface LocationSearchResult {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
}

export interface FeedItem {
  id: string;
  userName: string;
  title: string;
  subtitle: string;
}

export interface WorkoutItem {
  id: string;
  title: string;
  distanceKm: number;
  durationMin: number;
  profileType: ProfileType;
  dateLabel: string;
}