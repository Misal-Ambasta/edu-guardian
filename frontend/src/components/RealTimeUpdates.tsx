import { useEffect } from 'react';
import { useEmotionStore } from '../store/emotionStore';

interface RealTimeConfig {
  enabled: boolean;
  updateInterval: number;
  onUpdate?: () => void;
}

export const useRealTimeUpdates = ({ enabled = true, updateInterval = 5000, onUpdate }: RealTimeConfig) => {
  const { fetchStudentEmotions, currentStudentEmotion } = useEmotionStore();

  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    fetchStudentEmotions(currentStudentEmotion?.studentId || '');

    // Setup polling interval
    const intervalId = setInterval(() => {
      fetchStudentEmotions(currentStudentEmotion?.studentId || '');
      onUpdate?.();
    }, updateInterval);

    // Cleanup
    return () => clearInterval(intervalId);
  }, [enabled, updateInterval, fetchStudentEmotions, currentStudentEmotion?.studentId, onUpdate]);

  return {
    lastUpdated: new Date().toISOString(),
    isEnabled: enabled
  };
};

// WebSocket setup for real-time updates
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  private url: string;
  private onMessage: (data: any) => void;

  constructor(url: string, onMessage: (data: any) => void) {
    this.url = url;
    this.onMessage = onMessage;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.reconnect();
    }
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
