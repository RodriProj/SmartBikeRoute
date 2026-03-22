import { Flame, Home, Leaf, Map as MapIcon, PlayCircle, Shield, User } from 'lucide-react-native';
import React, { useState } from 'react';
import { ActivityIndicator, Alert, SafeAreaView, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import MapView, { PROVIDER_GOOGLE, Polyline } from 'react-native-maps';

export default function SmartBikeApp() {
  // --- ESTADOS GLOBAIS ---
  const [activeTab, setActiveTab] = useState('Mapa');
  const [selectedMode, setSelectedMode] = useState('Sem Suor');
  const [routeCoordinates, setRouteCoordinates] = useState([]); 
  const [loading, setLoading] = useState(false);

  // --- LIGAÇÃO AO BACKEND DO RODRIGO (NGROK) ---
const obterRotaReal = async (modo: string) => {
    setLoading(true);
    try {
      const response = await fetch('https://chemic-quiana-overhomely.ngrok-free.dev/routes/generate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          startLat: 41.2995, 
          startLon: -7.7448,
          endLat: 41.3015,
          endLon: -7.7395,
          profile_type: modo === 'Desafio' ? 'treino' : 'lazer',
          target_distance_km: 1,
          elevation_preference: modo === 'Sem Suor' ? 'baixa' : 'media',
          scenic_preference: 'media',
          traffic_avoidance: modo === 'Seguro' ? 'alta' : 'media',
          loop: false,
          training_goal: "string"
        }),
      });

      const data = await response.json();
      
      // --- DEBUG: Vê o que o Rodrigo está a enviar no teu terminal do VS Code ---
      console.log("DADOS RECEBIDOS:", JSON.stringify(data).substring(0, 200));

      // Tentamos encontrar as coordenadas em dois caminhos possíveis
      const rotaFinal = data.route?.features || data.features;

      if (rotaFinal && rotaFinal.length > 0) {
        const coordsRaw = rotaFinal[0].geometry.coordinates;
        
        // TESTE DE INVERSÃO: Se não der de uma forma, tenta a outra
        const pontos = coordsRaw.map((coord: any) => ({
          latitude: coord[1], // Tenta inverter aqui se não aparecer (GeoJSON padrão é Lon, Lat)
          longitude: coord[0],
        }));

        console.log("Pontos processados:", pontos.length);
        setRouteCoordinates(pontos);
        setActiveTab('Mapa');
      } else {
        Alert.alert("Aviso", "O servidor respondeu mas a lista de coordenadas veio vazia.");
      }
    } catch (error) {
      console.error("ERRO NO FETCH:", error);
      Alert.alert("Erro", "Não foi possível ligar ao servidor.");
    } finally {
      setLoading(false);
    }
  };
  // --- COMPONENTES DE ECRÃ ---
  const HomeScreen = () => (
    <ScrollView style={styles.screenContainer}>
      <Text style={styles.welcomeText}>Olá, Adriano! 👋</Text>
      <Text style={styles.subText}>Vila Real está pronta para a tua pedalada.</Text>
      <View style={styles.statsRow}>
        <View style={styles.statCard}><Text style={styles.statNumber}>12km</Text><Text style={styles.statLabel}>Hoje</Text></View>
        <View style={styles.statCard}><Text style={styles.statNumber}>45m</Text><Text style={styles.statLabel}>Tempo</Text></View>
      </View>
    </ScrollView>
  );

  const MapScreen = () => (
    <View style={styles.mapContainer}>
      <MapView
        provider={PROVIDER_GOOGLE}
        style={styles.map}
        initialRegion={{
          latitude: 41.2952,
          longitude: -7.7460,
          latitudeDelta: 0.02,
          longitudeDelta: 0.02,
        }}
      >
        {routeCoordinates.length > 0 && (
          <Polyline 
            coordinates={routeCoordinates} 
            strokeColor="#1EB1FC" 
            strokeWidth={6} 
          />
        )}
      </MapView>
      <View style={styles.mapOverlay}>
        <Text style={styles.overlayText}>Modo: {selectedMode}</Text>
      </View>
    </View>
  );

  const StartScreen = () => (
    <View style={styles.centered}>
      <Text style={styles.startHeader}>Planear Rota</Text>
      <View style={styles.innovationPanel}>
        <View style={styles.moodContainer}>
          {['Sem Suor', 'Desafio', 'Seguro'].map((mode) => (
            <TouchableOpacity 
              key={mode}
              style={[styles.moodBtn, selectedMode === mode && styles.activeMood]} 
              onPress={() => setSelectedMode(mode)}
            >
              {mode === 'Sem Suor' && <Leaf size={24} color={selectedMode === mode ? '#1EB1FC' : '#666'} />}
              {mode === 'Desafio' && <Flame size={24} color={selectedMode === mode ? '#1EB1FC' : '#666'} />}
              {mode === 'Seguro' && <Shield size={24} color={selectedMode === mode ? '#1EB1FC' : '#666'} />}
              <Text style={styles.moodLabel}>{mode}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <TouchableOpacity 
        style={styles.startRoundButton} 
        onPress={() => obterRotaReal(selectedMode)}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator size="large" color="#1EB1FC" />
        ) : (
          <>
            <PlayCircle size={100} color="white" fill="#1EB1FC" />
            <Text style={styles.startBtnText}>INICIAR {selectedMode.toUpperCase()}</Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );

  const ProfileScreen = () => (
    <ScrollView style={styles.screenContainer}>
      <View style={styles.profileHeader}>
        <View style={styles.avatarCircle}><User size={50} color="#1EB1FC" /></View>
        <Text style={styles.profileName}>Adriano & Rodrigo</Text>
        <Text style={styles.profileLocation}>Vila Real • Ciclista Multi-Perfil</Text>
      </View>
      <Text style={styles.sectionTitle}>Histórico de Perfil Ativo: {selectedMode}</Text>
      <Text style={styles.subText}>Os dados de impacto mudam conforme o modo selecionado.</Text>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {activeTab === 'Início' && <HomeScreen />}
        {activeTab === 'Mapa' && <MapScreen />}
        {activeTab === 'Começar' && <StartScreen />}
        {activeTab === 'Perfil' && <ProfileScreen />}
      </View>

      <View style={styles.tabBar}>
        <TabItem label="Início" icon={<Home size={24} />} active={activeTab === 'Início'} onPress={() => setActiveTab('Início')} />
        <TabItem label="Mapa" icon={<MapIcon size={24} />} active={activeTab === 'Mapa'} onPress={() => setActiveTab('Mapa')} />
        <TabItem label="Começar" icon={<PlayCircle size={32} />} active={activeTab === 'Começar'} onPress={() => setActiveTab('Começar')} />
        <TabItem label="Perfil" icon={<User size={24} />} active={activeTab === 'Perfil'} onPress={() => setActiveTab('Perfil')} />
      </View>
    </SafeAreaView>
  );
}

const TabItem = ({label, icon, active, onPress}: any) => (
  <TouchableOpacity style={styles.tabItem} onPress={onPress}>
    {React.cloneElement(icon, { color: active ? '#1EB1FC' : '#999' })}
    <Text style={[styles.tabLabel, {color: active ? '#1EB1FC' : '#999'}]}>{label}</Text>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  content: { flex: 1 },
  screenContainer: { flex: 1, padding: 25 },
  welcomeText: { fontSize: 26, fontWeight: 'bold', color: '#333' },
  subText: { fontSize: 15, color: '#666', marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 25 },
  statCard: { backgroundColor: '#F0F9FF', padding: 20, borderRadius: 15, width: '48%', alignItems: 'center' },
  statNumber: { fontSize: 22, fontWeight: 'bold', color: '#1EB1FC' },
  statLabel: { color: '#666' },
  mapContainer: { flex: 1 },
  map: { ...StyleSheet.absoluteFillObject },
  mapOverlay: { position: 'absolute', top: 50, alignSelf: 'center', backgroundColor: 'white', padding: 10, borderRadius: 20, elevation: 5 },
  overlayText: { fontWeight: 'bold', color: '#1EB1FC' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  startHeader: { fontSize: 24, fontWeight: 'bold', marginBottom: 30 },
  innovationPanel: { backgroundColor: '#F8F9FA', padding: 20, borderRadius: 25, width: '100%', marginBottom: 40 },
  moodContainer: { flexDirection: 'row', justifyContent: 'space-around' },
  moodBtn: { alignItems: 'center', padding: 15, borderRadius: 20, backgroundColor: '#FFF', width: 90, elevation: 2 },
  activeMood: { borderColor: '#1EB1FC', borderWidth: 2, backgroundColor: '#E6F4FE' },
  moodLabel: { fontSize: 10, marginTop: 8, fontWeight: '700' },
  startRoundButton: { alignItems: 'center' },
  startBtnText: { marginTop: 15, fontSize: 18, fontWeight: '900', color: '#1EB1FC' },
  profileHeader: { alignItems: 'center', marginBottom: 20 },
  avatarCircle: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#E6F4FE', justifyContent: 'center', alignItems: 'center', marginBottom: 10 },
  profileName: { fontSize: 20, fontWeight: 'bold' },
  profileLocation: { color: '#999', fontSize: 12 },
  tabBar: { flexDirection: 'row', height: 75, borderTopWidth: 1, borderTopColor: '#EEE', justifyContent: 'space-around', alignItems: 'center' },
  tabItem: { alignItems: 'center' },
  tabLabel: { fontSize: 10, marginTop: 4 }
});