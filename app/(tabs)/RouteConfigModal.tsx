import { ChevronDown, ChevronUp, X } from 'lucide-react-native';
import React from 'react';
import {
    ActivityIndicator,
    Modal,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Switch,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import { COMPETITION_GOALS, EXERCISE_GOALS } from './api';
import {
    CompetitionGoal,
    DifficultyLevel,
    EnvironmentPreference,
    ExerciseGoal,
    PreferenceLevel,
    ProfileType,
    RouteFormState,
    SurfacePreference,
} from './types';

interface Props {
  visible: boolean;
  loading: boolean;
  showAdvanced: boolean;
  setShowAdvanced: React.Dispatch<React.SetStateAction<boolean>>;
  form: RouteFormState;
  setForm: React.Dispatch<React.SetStateAction<RouteFormState>>;
  onClose: () => void;
  onSubmit: () => void;
  onClearRoute: () => void;
}

export default function RouteConfigModal({
  visible,
  loading,
  showAdvanced,
  setShowAdvanced,
  form,
  setForm,
  onClose,
  onSubmit,
  onClearRoute,
}: Props) {
  const updateForm = <K extends keyof RouteFormState>(key: K, value: RouteFormState[K]) => {
    setForm((prev) => {
      const next = { ...prev, [key]: value };

      if (key === 'profile_type') {
        if (value === 'lazer') {
          next.training_goal = null;
          next.intensity_preference = 'media';
          next.route_fluency = 'media';
        }

        if (value === 'exercicio') {
          next.training_goal = 'queimar_gordura';
          next.intensity_preference = 'media';
          next.route_fluency = 'media';
        }

        if (value === 'competicao') {
          next.training_goal = 'velocidade';
          next.intensity_preference = 'alta';
          next.route_fluency = 'alta';
        }
      }

      return next;
    });
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Configuração da rota</Text>
          <TouchableOpacity onPress={onClose}>
            <X size={26} color="#333" />
          </TouchableOpacity>
        </View>

        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Perfil principal</Text>

            <Selector
              label="Modo"
              current={form.profile_type}
              options={['lazer', 'exercicio', 'competicao']}
              onSelect={(value: ProfileType) => updateForm('profile_type', value)}
            />

            <View style={styles.inputRow}>
              <Text style={styles.inputLabel}>Distância alvo (km)</Text>
              <TextInput
                keyboardType="numeric"
                style={styles.numberInput}
                value={String(form.target_distance_km)}
                onChangeText={(value) => updateForm('target_distance_km', Number(value || 0))}
              />
            </View>

            <View style={styles.switchRow}>
              <Text style={styles.inputLabel}>Voltar ao ponto inicial</Text>
              <Switch
                value={form.loop}
                onValueChange={(value) => updateForm('loop', value)}
              />
            </View>
          </View>

          <View style={styles.card}>
            <TouchableOpacity style={styles.advancedHeader} onPress={() => setShowAdvanced((prev) => !prev)}>
              <Text style={styles.sectionTitle}>Opções avançadas</Text>
              {showAdvanced ? <ChevronUp size={20} color="#1EB1FC" /> : <ChevronDown size={20} color="#1EB1FC" />}
            </TouchableOpacity>

            {showAdvanced && (
              <View style={styles.advancedContent}>
                <Selector
                  label="Subidas"
                  current={form.elevation_preference}
                  options={['baixa', 'media', 'alta']}
                  onSelect={(value: PreferenceLevel) => updateForm('elevation_preference', value)}
                />

                <Selector
                  label="Paisagem"
                  current={form.scenic_preference}
                  options={['baixa', 'media', 'alta']}
                  onSelect={(value: PreferenceLevel) => updateForm('scenic_preference', value)}
                />

                <Selector
                  label="Evitar trânsito"
                  current={form.traffic_avoidance}
                  options={['baixa', 'media', 'alta']}
                  onSelect={(value: PreferenceLevel) => updateForm('traffic_avoidance', value)}
                />

                <Selector
                  label="Ambiente"
                  current={form.environment_preference}
                  options={['urbana', 'rural', 'mista']}
                  onSelect={(value: EnvironmentPreference) => updateForm('environment_preference', value)}
                />

                <Selector
                  label="Piso"
                  current={form.surface_preference}
                  options={['asfalto', 'asfalto_ecovia', 'indiferente']}
                  onSelect={(value: SurfacePreference) => updateForm('surface_preference', value)}
                />

                {form.profile_type === 'lazer' && (
                  <>
                    <Selector
                      label="Dificuldade"
                      current={form.difficulty_level}
                      options={['muito_facil', 'facil', 'moderada']}
                      onSelect={(value: DifficultyLevel) => updateForm('difficulty_level', value)}
                    />

                    <Selector
                      label="Pontos de interesse"
                      current={form.points_of_interest_preference}
                      options={['baixa', 'media', 'alta']}
                      onSelect={(value: PreferenceLevel) =>
                        updateForm('points_of_interest_preference', value)
                      }
                    />

                    <Selector
                      label="Zonas verdes"
                      current={form.green_area_preference}
                      options={['baixa', 'media', 'alta']}
                      onSelect={(value: PreferenceLevel) => updateForm('green_area_preference', value)}
                    />
                  </>
                )}

                {form.profile_type === 'exercicio' && (
                  <>
                    <Selector
                      label="Intensidade"
                      current={form.intensity_preference}
                      options={['baixa', 'media', 'alta']}
                      onSelect={(value: PreferenceLevel) => updateForm('intensity_preference', value)}
                    />

                    <Selector
                      label="Objetivo"
                      current={form.training_goal}
                      options={EXERCISE_GOALS as unknown as string[]}
                      onSelect={(value: ExerciseGoal) => updateForm('training_goal', value)}
                    />
                  </>
                )}

                {form.profile_type === 'competicao' && (
                  <>
                    <Selector
                      label="Intensidade"
                      current={form.intensity_preference}
                      options={['baixa', 'media', 'alta']}
                      onSelect={(value: PreferenceLevel) => updateForm('intensity_preference', value)}
                    />

                    <Selector
                      label="Fluidez"
                      current={form.route_fluency}
                      options={['baixa', 'media', 'alta']}
                      onSelect={(value: PreferenceLevel) => updateForm('route_fluency', value)}
                    />

                    <Selector
                      label="Objetivo"
                      current={form.training_goal}
                      options={COMPETITION_GOALS as unknown as string[]}
                      onSelect={(value: CompetitionGoal) => updateForm('training_goal', value)}
                    />
                  </>
                )}
              </View>
            )}
          </View>

          <TouchableOpacity style={styles.mainButton} onPress={onSubmit}>
            {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.mainButtonText}>Gerar rota</Text>}
          </TouchableOpacity>

          <TouchableOpacity style={styles.ghostButton} onPress={onClearRoute}>
            <Text style={styles.ghostButtonText}>Limpar rota atual</Text>
          </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}

function Selector({
  label,
  current,
  options,
  onSelect,
}: {
  label: string;
  current: string | null;
  options: string[];
  onSelect: (value: any) => void;
}) {
  return (
    <View style={styles.selectorContainer}>
      <Text style={styles.selectorLabel}>{label}</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {options.map((option) => {
          const active = current === option;

          return (
            <TouchableOpacity
              key={option}
              style={[styles.optionButton, active && styles.optionButtonActive]}
              onPress={() => onSelect(option)}
            >
              <Text style={[styles.optionText, active && styles.optionTextActive]}>
                {option.replaceAll('_', ' ')}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F8FB',
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 20,
    paddingVertical: 18,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: '800',
    color: '#111827',
  },
  content: {
    padding: 12,
    paddingBottom: 36,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
  },
  advancedHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  advancedContent: {
    marginTop: 8,
  },
  selectorContainer: {
    marginTop: 14,
  },
  selectorLabel: {
    fontSize: 11,
    fontWeight: '800',
    color: '#9CA3AF',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  optionButton: {
    backgroundColor: '#EEF2F7',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 12,
    marginRight: 8,
  },
  optionButtonActive: {
    backgroundColor: '#1EB1FC',
  },
  optionText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#4B5563',
  },
  optionTextActive: {
    color: '#FFFFFF',
  },
  inputRow: {
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  switchRow: {
    marginTop: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  numberInput: {
    width: 80,
    backgroundColor: '#EEF2F7',
    borderRadius: 12,
    textAlign: 'center',
    paddingVertical: 10,
    fontWeight: '700',
    color: '#111827',
  },
  mainButton: {
    backgroundColor: '#1EB1FC',
    borderRadius: 18,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 4,
  },
  mainButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '800',
  },
  ghostButton: {
    marginTop: 10,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 18,
    backgroundColor: '#FFFFFF',
  },
  ghostButtonText: {
    color: '#4B5563',
    fontWeight: '700',
  },
});