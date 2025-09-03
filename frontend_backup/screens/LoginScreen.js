import React, { useContext, useEffect } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BotContext } from '../App'; // Adjust path based on your structure

export default function LoginScreen() {
  const { isAuthenticated, setIsAuthenticated } = useContext(BotContext);

  useEffect(() => {
    // Check authentication status from file or AsyncStorage
    const checkAuthStatus = async () => {
      try {
        const response = await fetch('http://localhost:8081/flex_auth_status.txt'); // Adjust URL if needed
        const status = await response.text();
        if (status === 'true') {
          await AsyncStorage.setItem('flexAuthenticated', 'true');
          setIsAuthenticated(true);
          Alert.alert('Success', 'Flex authentication detected!');
        } else {
          await AsyncStorage.setItem('flexAuthenticated', 'false');
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        setIsAuthenticated(false);
      }
    };
    checkAuthStatus();
  }, [setIsAuthenticated]);

  const saveData = async () => {
    try {
      await AsyncStorage.setItem('userToken', 'exampleToken');
      console.log('Data saved successfully');
    } catch (error) {
      console.error('Error saving data:', error);
    }
  };

  return (
    <View>
      <Text>Login Screen</Text>
      <Button title="Save Token" onPress={saveData} />
      <Text>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</Text>
    </View>
  );
}