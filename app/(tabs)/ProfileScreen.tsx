import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { WorkoutItem } from './types';

const DEFAULT_WORKOUTS: WorkoutItem[] = [
  {
    id: '1',
    title: 'Treino exercício',
    distanceKm: 18.4,
    durationMin: 52,
    profileType: 'exercicio',
    dateLabel: 'Ontem',
  },
  {
    id: '2',
    title: 'Percurso lazer',
    distanceKm: 12.1,
    durationMin: 41,
    profileType: 'lazer',
    dateLabel: 'Há 3 dias',
  },
  {
    id: '3',
    title: 'Sessão competição',
    distanceKm: 28.9,
    durationMin: 63,
    profileType: 'competicao',
    dateLabel: 'Semana passada',
  },
];

export default function ProfileScreen({ workouts = DEFAULT_WORKOUTS }: { workouts?: WorkoutItem[] }) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Perfil</Text>
      <Text style={styles.subtitle}>
        Área preparada para histórico de treinos, comparação de desempenho e evolução do utilizador.
      </Text>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Resumo geral</Text>
        <Text style={styles.summaryText}>Treinos executados: 28</Text>
        <Text style={styles.summaryText}>Distância total: 642 km</Text>
        <Text style={styles.summaryText}>Tempo acumulado: 34h 20m</Text>
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Melhorias</Text>
        <Text style={styles.summaryText}>Últimos 7 dias vs últimos 30 dias</Text>
        <Text style={styles.summaryText}>+12% distância</Text>
        <Text style={styles.summaryText}>+8% ritmo médio</Text>
      </View>

      <Text style={styles.sectionTitle}>Treinos recentes</Text>

      {workouts.map((workout) => (
        <View key={workout.id} style={styles.workoutCard}>
          <Text style={styles.workoutTitle}>{workout.title}</Text>
          <Text style={styles.workoutText}>Perfil: {workout.profileType}</Text>
          <Text style={styles.workoutText}>Distância: {workout.distanceKm} km</Text>
          <Text style={styles.workoutText}>Duração: {workout.durationMin} min</Text>
          <Text style={styles.workoutDate}>{workout.dateLabel}</Text>
        </View>
      ))}

      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Integração futura com backend</Text>
        <Text style={styles.infoText}>
          Este ecrã está pronto para consumir endpoints como <Text style={styles.code}>GET /profile/workouts</Text>,{' '}
          <Text style={styles.code}>GET /profile/summary</Text> e <Text style={styles.code}>GET /profile/progress</Text>.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingBottom: 120,
    backgroundColor: '#F6F8FB',
  },
  title: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 20,
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  summaryText: {
    fontSize: 14,
    color: '#4B5563',
    marginBottom: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
    marginTop: 6,
    marginBottom: 12,
  },
  workoutCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
  },
  workoutTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  workoutText: {
    fontSize: 14,
    color: '#4B5563',
    marginBottom: 4,
  },
  workoutDate: {
    marginTop: 8,
    fontSize: 12,
    color: '#9CA3AF',
    fontWeight: '700',
  },
  infoCard: {
    backgroundColor: '#EEF7FF',
    borderRadius: 18,
    padding: 16,
    marginTop: 8,
  },
  infoTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  code: {
    fontWeight: '800',
    color: '#1EB1FC',
  },
});