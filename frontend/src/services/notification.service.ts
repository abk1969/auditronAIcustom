import api from './api';

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  link?: string;
  metadata?: Record<string, any>;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  desktop: boolean;
  auditCompletion: boolean;
  criticalIssues: boolean;
  weeklyReport: boolean;
  systemUpdates: boolean;
}

class NotificationService {
  private websocket: WebSocket | null = null;

  constructor() {
    this.initializeWebSocket();
  }

  private initializeWebSocket() {
    const token = localStorage.getItem('token');
    if (token) {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
      this.websocket = new WebSocket(`${wsUrl}/notifications?token=${token}`);

      this.websocket.onmessage = (event) => {
        const notification = JSON.parse(event.data);
        this.showNotification(notification);
      };

      this.websocket.onclose = () => {
        // Tentative de reconnexion après 5 secondes
        setTimeout(() => this.initializeWebSocket(), 5000);
      };
    }
  }

  private showNotification(notification: Notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/logo192.png',
      });
    }
  }

  async requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    return false;
  }

  async getNotifications(params?: {
    unreadOnly?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<{ notifications: Notification[]; total: number }> {
    const response = await api.get('/notifications', { params });
    return response.data;
  }

  async markAsRead(notificationId: string): Promise<void> {
    await api.patch(`/notifications/${notificationId}/read`);
  }

  async markAllAsRead(): Promise<void> {
    await api.post('/notifications/mark-all-read');
  }

  async deleteNotification(notificationId: string): Promise<void> {
    await api.delete(`/notifications/${notificationId}`);
  }

  async clearAllNotifications(): Promise<void> {
    await api.delete('/notifications');
  }

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    const response = await api.get('/notifications/preferences');
    return response.data;
  }

  async updateNotificationPreferences(
    preferences: Partial<NotificationPreferences>
  ): Promise<NotificationPreferences> {
    const response = await api.patch('/notifications/preferences', preferences);
    return response.data;
  }

  async testNotification(): Promise<void> {
    await api.post('/notifications/test');
  }

  disconnect(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}

export const notificationService = new NotificationService(); 