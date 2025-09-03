import React, { useEffect, useState, useContext } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import axios from 'axios';
import { BotContext } from '../App';

const BASE_URL = 'http://192.168.1.221:8000';

export default function DashboardScreen() {
  const { botStatus } = useContext(BotContext);
  const [metrics, setMetrics] = useState({ blocksGrabbed: 0, earnings: 0, history: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${BASE_URL}/metrics`);
        setMetrics(res.data || { blocksGrabbed: 0, earnings: 0, history: [] });
      } catch (error) {
        console.log('Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Bot Dashboard</Text>
      <Text style={styles.status}>
        Status: <Text style={botStatus === 'running' ? styles.running : styles.stopped}>
          {botStatus}
        </Text>
      </Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />
      ) : (
        <>
          <Text style={styles.metric}>Blocks Grabbed: {metrics.blocksGrabbed}</Text>
          <Text style={styles.metric}>Earnings: ${metrics.earnings.toFixed(2)}</Text>
          {metrics.history.length > 0 && (
            <View style={styles.chartContainer}>
              <Text style={styles.chartTitle}>Earnings Trend</Text>
              <Text style={styles.chartText}>
                Day 1: ${metrics.history[0]?.earnings || 0}, Day 2: ${metrics.history[1]?.earnings || 0}, Day 3: ${metrics.earnings.toFixed(2)}
              </Text>
            </View>
          )}
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  status: {
    fontSize: 16,
    marginBottom: 15,
    color: '#333',
  },
  running: {
    color: '#2ECC71',
    fontWeight: 'bold',
  },
  stopped: {
    color: '#E74C3C',
    fontWeight: 'bold',
  },
  metric: {
    fontSize: 18,
    color: '#333',
    marginBottom: 10,
  },
  loader: {
    marginTop: 20,
  },
  chartContainer: {
    marginTop: 20,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  chartText: {
    fontSize: 14,
    color: '#666',
  },
});