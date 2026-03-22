import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { FeedItem } from './types';

const DEFAULT_FEED: FeedItem[] = [
  {
    id: '1',
    userName: 'João',
    title: 'Terminou um treino em modo exercício',
    subtitle: '22 km · objetivo: ganhar resistência',
  },
  {
    id: '2',
    userName: 'Marta',
    title: 'Partilhou uma rota em modo lazer',
    subtitle: 'Percurso panorâmico com baixa dificuldade',
  },
  {
    id: '3',
    userName: 'Tiago',
    title: 'Fez uma saída em modo competição',
    subtitle: 'Foco em velocidade e ritmo constante',
  },
];

export default function HomeScreen({ feed = DEFAULT_FEED }: { feed?: FeedItem[] }) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Home</Text>
      <Text style={styles.subtitle}>
        Feed preparado para mostrar atividade dos amigos, rotas partilhadas e destaques da comunidade.
      </Text>

      {feed.map((item) => (
        <View key={item.id} style={styles.card}>
          <Text style={styles.userName}>{item.userName}</Text>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <Text style={styles.cardSubtitle}>{item.subtitle}</Text>
        </View>
      ))}

      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>Integração futura com backend</Text>
        <Text style={styles.infoText}>
          Este ecrã está pronto para consumir um endpoint como <Text style={styles.code}>GET /feed</Text>.
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
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 18,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
  },
  userName: {
    fontSize: 12,
    fontWeight: '800',
    color: '#1EB1FC',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 6,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#4B5563',
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