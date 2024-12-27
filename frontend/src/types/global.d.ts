/// <reference types="react" />
/// <reference types="react-dom" />

declare module '*.svg' {
  const content: React.FunctionComponent<React.SVGAttributes<SVGElement>>;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.json' {
  const content: { [key: string]: any };
  export default content;
}

interface Window {
  gtag: (
    command: 'event' | 'config' | 'set',
    targetId: string,
    params?: {
      event_category?: string;
      event_label?: string;
      value?: number;
      [key: string]: any;
    }
  ) => void;
}

declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: 'development' | 'production' | 'test';
    REACT_APP_API_URL: string;
    REACT_APP_WS_URL: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_ANALYTICS_ID?: string;
    REACT_APP_ENABLE_ANALYTICS?: string;
    REACT_APP_VERSION: string;
  }
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
} 