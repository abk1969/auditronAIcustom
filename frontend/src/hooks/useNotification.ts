"""Hook personnalisé pour la gestion des notifications."""
import { useState, createContext, useContext, useCallback } from 'react';
import { useSnackbar, VariantType } from 'notistack';

interface NotificationContextType {
  showNotification: (message: string, type?: VariantType) => void;
  notifications: Notification[];
  markAsRead: (id: string) => void;
  clearAll: () => void;
}

interface Notification {
  id: string;
  message: string;
  type: VariantType;
  timestamp: number;
  read: boolean;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const { enqueueSnackbar } = useSnackbar();

  const showNotification = useCallback((message: string, type: VariantType = 'default') => {
    const notification: Notification = {
      id: Date.now().toString(),
      message,
      type,
      timestamp: Date.now(),
      read: false
    };

    setNotifications(prev => [notification, ...prev]);
    enqueueSnackbar(message, { variant: type });
  }, [enqueueSnackbar]);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      )
    );
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        showNotification,
        notifications,
        markAsRead,
        clearAll
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}; 