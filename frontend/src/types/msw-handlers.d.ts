import { HttpHandler } from 'msw';

export interface MockRequest<T = any> {
  request: Request & {
    json(): Promise<T>;
  };
}

export type MockHandler = HttpHandler;

declare module 'msw' {
  interface RequestHandler {
    (info: MockRequest): Promise<Response> | Response;
  }
} 