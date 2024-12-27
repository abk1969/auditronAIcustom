import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

async function prepare() {
  if (process.env.NODE_ENV === 'development' && !process.env.DISABLE_MSW) {
    const { worker } = await import('./mocks/browser');
    return worker.start({
      onUnhandledRequest: 'bypass',
    });
  }
  return Promise.resolve();
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

prepare().then(() => {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}).catch(console.error);
