"""Service de gestion des connexions WebSocket."""
import { io, Socket } from 'socket.io-client';
import { useNotification } from '../hooks/useNotification';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private readonly showNotification: any;

  constructor() {
    const { showNotification } = useNotification();
    this.showNotification = showNotification;
  }

  connect() {
    if (this.socket?.connected) return;

    this.socket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:3001', {
      auth: {
        token: localStorage.getItem('auth_token')
      },
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      this.reconnectAttempts = 0;
      this.showNotification('Connexion WebSocket établie', 'success');
    });

    this.socket.on('disconnect', (reason) => {
      if (reason === 'io server disconnect') {
        this.connect();
      }
      this.showNotification('Connexion WebSocket perdue', 'warning');
    });

    this.socket.on('connect_error', () => {
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.showNotification(
          'Impossible de se connecter au serveur WebSocket',
          'error'
        );
      }
    });

    // Événements métier
    this.socket.on('analysis_progress', (data) => {
      // Gérer la progression de l'analyse
    });

    this.socket.on('new_alert', (data) => {
      this.showNotification(
        `Nouvelle alerte : ${data.message}`,
        data.severity
      );
    });

    this.socket.on('resource_update', (data) => {
      // Mettre à jour les métriques de ressources
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Méthodes d'émission d'événements
  startAnalysis(data: any) {
    this.socket?.emit('start_analysis', data);
  }

  subscribeToAlerts() {
    this.socket?.emit('subscribe_alerts');
  }

  unsubscribeFromAlerts() {
    this.socket?.emit('unsubscribe_alerts');
  }

  subscribeToResources() {
    this.socket?.emit('subscribe_resources');
  }

  unsubscribeFromResources() {
    this.socket?.emit('unsubscribe_resources');
  }
}

export const wsService = new WebSocketService(); 