import { Flame, Home, Leaf, Map as MapIcon, PlayCircle, Shield, User } from 'lucide-react-native';
import React, { useRef, useState } from 'react';
import { ActivityIndicator, Alert, SafeAreaView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE, Polyline } from 'react-native-maps';

const API_BASE = 'https://chemic-quiana-overhomely.ngrok-free.dev';

export default function SmartBikeApp() {
  const [activeTab, setActiveTab] = useState('Começar');
  const [selectedMode, setSelectedMode] = useState('Lazer'); // Padrão: Lazer
  const [routeCoordinates, setRouteCoordinates] = useState([]); 
  const [loading, setLoading] = useState(false);
  const mapRef = useRef<MapView>(null);

  const obterRotaReal = async (modo: string) => {
    setLoading(true);
    setRouteCoordinates([]);

    // Mapeamento direto para as chaves que o Rodrigo usa
    const modoBackend = modo.toLowerCase(); // Converte 'Lazer' para 'lazer', etc.

    const payload = {
      startLat: 41.2952,
      startLon: -7.7460,
      endLat: 41.3005,
      endLon: -7.7398,
      profile_type: modoBackend, // Envia exatamente 'lazer', 'exercicio' ou 'competicao'
      target_distance_km: 5,
      elevation_preference: modoBackend === 'lazer' ? "baixa" : (modoBackend === 'exercicio' ? "media" : "alta"),
      scenic_preference: "alta",
      traffic_avoidance: modoBackend === 'lazer' ? "alta" : "media",
      loop: false,
      training_goal: modoBackend === 'competicao' ? "performance" : "fitness"
    };

    try {
      const response = await fetch(`${API_BASE}/routes/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      const rotaFeatures = data.route?.features || data.features;

      if (rotaFeatures && rotaFeatures.length > 0) {
        const geometria = rotaFeatures[0].geometry;
        const pontosFormatados = geometria.coordinates.map((coord: any) => ({
          latitude: coord[1],
          longitude: coord[0],
        }));

        setRouteCoordinates(pontosFormatados);
        setActiveTab('Mapa');

        setTimeout(() => {
          mapRef.current?.fitToCoordinates(pontosFormatados, {
            edgePadding: { top: 60, right: 60, bottom: 60, left: 60 },
            animated: true,
          });
        }, 600);
      } else {
        Alert.alert("Aviso", "O servidor não encontrou uma rota para este perfil.");
      }
    } catch (error) {
      Alert.alert("Erro de Rede", "Não foi possível ligar ao servidor.");
    } finally {
      setLoading(false);
    }
  };

  // Define a cor da linha com base no modo
  const getRouteColor = () => {
    switch(selectedMode) {
      case 'Lazer': return '#2ECC71';      // Verde
      case 'Exercicio': return '#1EB1FC';  // Azul
      case 'Competicao': return '#E74C3C'; // Vermelho
      default: return '#1EB1FC';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {activeTab === 'Mapa' ? (
          <View style={styles.full}>
            <MapView
              ref={mapRef}
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
                <>
                  <Polyline 
                    coordinates={routeCoordinates} 
                    strokeColor={getRouteColor()} 
                    strokeWidth={6} 
                  />
                  <Marker coordinate={routeCoordinates[0]} title="Partida" pinColor="green" />
                  <Marker coordinate={routeCoordinates[routeCoordinates.length - 1]} title="Destino" pinColor="black" />
                </>
              )}
            </MapView>
          </View>
        ) : activeTab === 'Começar' ? (
          <View style={styles.center}>
            <Text style={styles.title}>Modos de Ciclismo</Text>
            <View style={styles.row}>
              <ModeBtn label="Lazer" active={selectedMode === 'Lazer'} icon={<Leaf size={24}/>} onSelect={() => setSelectedMode('Lazer')} />
              <ModeBtn label="Exercicio" active={selectedMode === 'Exercicio'} icon={<Flame size={24}/>} onSelect={() => setSelectedMode('Exercicio')} />
              <ModeBtn label="Competicao" active={selectedMode === 'Competicao'} icon={<Shield size={24}/>} onSelect={() => setSelectedMode('Competicao')} />
            </View>
            <TouchableOpacity style={[styles.btn, {backgroundColor: getRouteColor()}]} onPress={() => obterRotaReal(selectedMode)}>
              {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.btnText}>PLANEAR PERCURSO</Text>}
            </TouchableOpacity>
          </View>
        ) : <View style={styles.center}><Text>Ecrã de Perfil</Text></View>}
      </View>

      <View style={styles.tabBar}>
        <Tab icon={<Home size={22}/>} active={activeTab === 'Início'} onPress={() => setActiveTab('Início')} />
        <Tab icon={<MapIcon size={22}/>} active={activeTab === 'Mapa'} onPress={() => setActiveTab('Mapa')} />
        <Tab icon={<PlayCircle size={30}/>} active={activeTab === 'Começar'} onPress={() => setActiveTab('Começar')} />
        <Tab icon={<User size={22}/>} active={activeTab === 'Perfil'} onPress={() => setActiveTab('Perfil')} />
      </View>
    </SafeAreaView>
  );
}

const ModeBtn = ({label, active, icon, onSelect}: any) => (
  <TouchableOpacity style={[styles.modeBtn, active && styles.activeMode]} onPress={onSelect}>
    {React.cloneElement(icon, { color: active ? '#333' : '#666' })}
    <Text style={[styles.modeLabel, active && {fontWeight: 'bold'}]}>{label}</Text>
  </TouchableOpacity>
);

const Tab = ({icon, active, onPress}: any) => (
  <TouchableOpacity style={styles.tab} onPress={onPress}>
    {React.cloneElement(icon, { color: active ? '#1EB1FC' : '#999' })}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  content: { flex: 1 },
  full: { flex: 1 },
  map: { ...StyleSheet.absoluteFillObject },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 25 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 40 },
  row: { flexDirection: 'row', justifyContent: 'space-between', width: '100%', marginBottom: 40 },
  modeBtn: { width: '31%', padding: 18, backgroundColor: '#F8F9FA', borderRadius: 20, alignItems: 'center', borderWidth: 1, borderColor: '#EEE' },
  activeMode: { borderColor: '#DDD', backgroundColor: '#F0F0F0', elevation: 2 },
  modeLabel: { fontSize: 10, marginTop: 8 },
  btn: { padding: 20, borderRadius: 30, width: '100%', alignItems: 'center', elevation: 3 },
  btnText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  tabBar: { flexDirection: 'row', height: 75, borderTopWidth: 1, borderColor: '#EEE', justifyContent: 'space-around', alignItems: 'center' },
  tab: { alignItems: 'center' }
});