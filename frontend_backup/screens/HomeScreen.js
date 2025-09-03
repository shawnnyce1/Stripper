import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView } from 'react-native';
import axios from 'axios';

export default function HomeScreen() {
  const [logs, setLogs] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('http://YOUR_LOCAL_IP:8000/status')
        .then(res => setLogs(res.data.logs))
        .catch(() => setLogs("Error fetching logs"));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ScrollView style={{ padding: 20 }}>
      <Text>{logs}</Text>
    </ScrollView>
  );
}

