import React, { useEffect, useState } from "react";
import { View, Text, Button, ActivityIndicator, Platform } from "react-native";
import axios from "axios";
import DeviceInfo from "react-native-device-info";
import Toast from "react-native-toast-message";

// Detect environment and set API base
const getBaseUrl = () => {
  if (Platform.OS === "android") {
    if (DeviceInfo.isEmulatorSync()) {
      return "http://10.0.2.2:8000"; // Android emulator -> host machine
    }
    return "http://192.168.1.221:8000"; // Physical device on LAN
  }
  if (Platform.OS === "ios") {
    if (DeviceInfo.isEmulatorSync()) {
      return "http://127.0.0.1:8000"; // iOS simulator
    }
    return "http://192.168.1.221:8000"; // iOS device on LAN
  }
  return "http://127.0.0.1:8000"; // Fallback
};

const BASE_URL = getBaseUrl();

export default function ConfigScreens({ navigation }) {
  const [authStatus, setAuthStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [botStatus, setBotStatus] = useState("stopped");

  const fetchAuthStatus = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/auth_status`);
      setAuthStatus(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/metrics`);
      setMetrics(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const startBot = async () => {
    if (!validateInputs()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${BASE_URL}/start_bot`, {
        days,
        hours,
        min_rate: parseFloat(minRate),
        warehouse,
      });
      if (response.data.success) {
        setBotStatus("running");
        Toast.show({
          type: "success",
          text1: "Success",
          text2: `Bot started for ${warehouse}!`,
        });
        navigation.navigate("Home");
      }
    } catch (error) {
      Toast.show({
        type: "error",
        text1: "Error",
        text2: "Failed to start bot",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuthStatus();
    fetchMetrics();
  }, []);

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 20, marginBottom: 10 }}>Amazon Flex Bot</Text>

      {authStatus ? (
        <Text>
          Authenticated: {authStatus.authenticated ? "✅ Yes" : "❌ No"} (
          {authStatus.message})
        </Text>
      ) : (
        <ActivityIndicator />
      )}

      <Button title="Start Bot" onPress={startBot} disabled={loading} />

      {metrics && (
        <View style={{ marginTop: 20 }}>
          <Text>Blocks Grabbed: {metrics.blocksGrabbed}</Text>
          <Text>Total Earnings: ${metrics.earnings}</Text>
          {metrics.history.map((h, i) => (
            <Text key={i}>
              {h.date}: ${h.earnings}
            </Text>
          ))}
        </View>
      )}
    </View>
  );
}
