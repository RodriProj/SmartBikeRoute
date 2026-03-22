import { Bike, Home, User } from 'lucide-react-native';
import React, { useState } from 'react';
import { SafeAreaView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import HomeScreen from './HomeScreen';
import ProfileScreen from './ProfileScreen';
import RideScreen from './RideScreen';
import { TabKey } from './types';

export default function IndexScreen() {
  const [activeTab, setActiveTab] = useState<TabKey>('Pedalar');

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {activeTab === 'Home' && <HomeScreen />}
        {activeTab === 'Pedalar' && <RideScreen />}
        {activeTab === 'Perfil' && <ProfileScreen />}
      </View>

      <View style={styles.tabBar}>
        <TabItem
          Icon={Home}
          label="Home"
          active={activeTab === 'Home'}
          onPress={() => setActiveTab('Home')}
        />
        <TabItem
          Icon={Bike}
          label="Pedalar"
          active={activeTab === 'Pedalar'}
          onPress={() => setActiveTab('Pedalar')}
        />
        <TabItem
          Icon={User}
          label="Perfil"
          active={activeTab === 'Perfil'}
          onPress={() => setActiveTab('Perfil')}
        />
      </View>
    </SafeAreaView>
  );
}

function TabItem({
  Icon,
  label,
  active,
  onPress,
}: {
  Icon: any;
  label: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.tabItem} onPress={onPress}>
      <Icon size={22} color={active ? '#1EB1FC' : '#999'} />
      <Text style={[styles.tabLabel, { color: active ? '#1EB1FC' : '#999' }]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F8FB',
  },
  content: {
    flex: 1,
  },
  tabBar: {
    height: 84,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabLabel: {
    marginTop: 4,
    fontSize: 11,
    fontWeight: '700',
  },
});