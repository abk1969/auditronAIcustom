/// <reference types="msw" />

import { DefaultBodyType } from 'msw';

declare module 'msw' {
  interface RequestHandler<
    RequestBodyType = DefaultBodyType,
    ResponseBodyType = DefaultBodyType
  > {
    request: Request & {
      json<T = RequestBodyType>(): Promise<T>;
      text(): Promise<string>;
    };
    params: Record<string, string>;
    cookies: Record<string, string>;
  }
}

declare global {
  interface Request {
    json<T = any>(): Promise<T>;
  }
} 