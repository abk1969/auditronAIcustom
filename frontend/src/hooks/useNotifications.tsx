import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Snackbar, Alert } from '@mui/material';
import {
  notificationService,
  Notification,
  NotificationPreferences,
} from '../services/notification.service';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  preferences: NotificationPreferences | null;
  loading: boolean;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
  updatePreferences: (prefs: Partial<NotificationPreferences>) => Promise<void>;
  requestPermission: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'info' | 'warning' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });

  useEffect(() => {
    loadNotifications();
    loadPreferences();
    requestPermission();
  }, []);

  const loadNotifications = async () => {
    try {
      const { notifications: newNotifications } = await notificationService.getNotifications({
        limit: 50,
      });
      setNotifications(newNotifications);
    } catch (error) {
      console.error('Erreur lors du chargement des notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPreferences = async () => {
    try {
      const prefs = await notificationService.getNotificationPreferences();
      setPreferences(prefs);
    } catch (error) {
      console.error('Erreur lors du chargement des préférences:', error);
    }
  };

  const requestPermission = async () => {
    try {
      const granted = await notificationService.requestNotificationPermission();
      if (granted) {
        showToast('Notifications activées avec succès', 'success');
      }
    } catch (error) {
      console.error('Erreur lors de la demande de permission:', error);
    }
  };

  const markAsRead = async (id: string) => {
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch (error) {
      showToast('Erreur lors du marquage de la notification', 'error');
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      showToast('Toutes les notifications ont été marquées comme lues', 'success');
    } catch (error) {
      showToast('Erreur lors du marquage des notifications', 'error');
    }
  };

  const deleteNotification = async (id: string) => {
    try {
      await notificationService.deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      showToast('Notification supprimée', 'success');
    } catch (error) {
      showToast('Erreur lors de la suppression de la notification', 'error');
    }
  };

  const clearAll = async () => {
    try {
      await notificationService.clearAllNotifications();
      setNotifications([]);
      showToast('Toutes les notifications ont été supprimées', 'success');
    } catch (error) {
      showToast('Erreur lors de la suppression des notifications', 'error');
    }
  };

  const updatePreferences = async (prefs: Partial<NotificationPreferences>) => {
    try {
      const updatedPrefs = await notificationService.updateNotificationPreferences(prefs);
      setPreferences(updatedPrefs);
      showToast('Préférences mises à jour avec succès', 'success');
    } catch (error) {
      showToast('Erreur lors de la mise à jour des préférences', 'error');
    }
  };

  const showToast = (message: string, severity: 'success' | 'info' | 'warning' | 'error') => {
    setToast({ open: true, message, severity });
  };

  const handleCloseToast = () => {
    setToast((prev) => ({ ...prev, open: false }));
  };

  const value = {
    notifications,
    unreadCount: notifications.filter((n) => !n.read).length,
    preferences,
    loading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    updatePreferences,
    requestPermission,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <Snackbar
        open={toast.open}
        autoHideDuration={6000}
        onClose={handleCloseToast}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseToast} severity={toast.severity} sx={{ width: '100%' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}; 