import React, { createContext, useState } from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, StyleSheet } from 'react-native';
import HomeScreen from './screens/HomeScreen';
import ConfigScreen from './screens/ConfigScreen';
import DashboardScreen from './screens/DashboardScreen';
import LoginScreen from './screens/LoginScreen'; // Added
import Ionicons from '@expo/vector-icons/Ionicons';

export const BotContext = createContext();

class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Something went wrong. Please restart the app.</Text>
        </View>
      );
    }
    return this.props.children;
  }
}

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: '#f5f5f5',
    primary: '#007AFF',
    text: '#333',
  },
};

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons = {
            Home: 'list',
            Config: 'settings',
            Dashboard: 'stats-chart',
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#666',
        tabBarStyle: { backgroundColor: '#f5f5f5' },
        headerStyle: { backgroundColor: '#f5f5f5' },
        headerTintColor: '#333',
        headerTitleStyle: { fontWeight: 'bold' },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: 'Bot Logs' }} />
      <Tab.Screen name="Config" component={ConfigScreen} options={{ title: 'Bot Configuration' }} />
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard' }} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [botStatus, setBotStatus] = useState('stopped');

  return (
    <ErrorBoundary>
      <BotContext.Provider value={{ botStatus, setBotStatus }}>
        <NavigationContainer theme={theme}>
          <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Main" component={MainTabs} />
          </Stack.Navigator>
        </NavigationContainer>
      </BotContext.Provider>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#D32F2F',
    textAlign: 'center',
  },
});