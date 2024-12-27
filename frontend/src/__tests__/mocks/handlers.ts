import { http, HttpResponse } from 'msw';
import { ApiResponse } from '../../types/api';

interface LoginBody {
  email: string;
  password: string;
}

interface RegisterBody {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

interface AuthResponse {
  token: string;
  user: {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
  };
}

interface ErrorResponse {
  message: string;
}

interface UserProfile {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
}

export const handlers = [
  http.post<never, LoginBody>('/auth/login', async ({ request }) => {
    const body = await request.json();
    
    if (body.email === 'test@example.com' && body.password === 'password123') {
      return HttpResponse.json<ApiResponse<AuthResponse>>({
        data: {
          token: 'fake-jwt-token',
          user: {
            id: 1,
            email: 'test@example.com',
            firstName: 'Test',
            lastName: 'User',
          },
        },
        status: 200,
      });
    }
    
    return HttpResponse.json<ApiResponse<ErrorResponse>>(
      {
        data: { message: 'Email ou mot de passe incorrect' },
        status: 401,
      },
      { status: 401 }
    );
  }),

  http.post<never, RegisterBody>('/auth/register', async ({ request }) => {
    const body = await request.json();
    
    return HttpResponse.json<ApiResponse<AuthResponse>>(
      {
        data: {
          token: 'fake-jwt-token',
          user: {
            id: 2,
            email: body.email,
            firstName: body.firstName,
            lastName: body.lastName,
          },
        },
        status: 201,
      },
      { status: 201 }
    );
  }),

  http.get<never, never>('/auth/me', async ({ request }) => {
    const token = request.headers.get('Authorization');
    
    if (!token || !token.startsWith('Bearer ')) {
      return HttpResponse.json<ApiResponse<ErrorResponse>>(
        {
          data: { message: 'Non authentifié' },
          status: 401,
        },
        { status: 401 }
      );
    }
    
    return HttpResponse.json<ApiResponse<UserProfile>>({
      data: {
        id: 1,
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
      },
      status: 200,
    });
  }),
]; 