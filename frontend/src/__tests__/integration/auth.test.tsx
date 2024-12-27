import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { MemoryRouter } from 'react-router-dom';
import { SignIn } from '../../components/auth/SignIn';
import { AuthProvider } from '../../hooks/useAuth';

interface LoginBody {
  email: string;
  password: string;
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

const server = setupServer(
  http.post<never, LoginBody>('/auth/login', async ({ request }) => {
    const body = await request.json();
    
    if (body.email === 'test@example.com' && body.password === 'password123') {
      return HttpResponse.json<AuthResponse>({
        token: 'fake-jwt-token',
        user: {
          id: 1,
          email: 'test@example.com',
          firstName: 'Test',
          lastName: 'User',
        },
      });
    }
    
    return HttpResponse.json<ErrorResponse>(
      { message: 'Email ou mot de passe incorrect' },
      { status: 401 }
    );
  })
);

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  server.resetHandlers();
  jest.clearAllMocks();
});

afterAll(() => {
  server.close();
});

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('SignIn Integration Tests', () => {
  const renderSignIn = () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <SignIn />
        </AuthProvider>
      </MemoryRouter>
    );
  };

  test('affiche un message d\'erreur pour des identifiants invalides', async () => {
    renderSignIn();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/mot de passe/i), {
      target: { value: 'wrongpassword' },
    });

    fireEvent.click(screen.getByText(/se connecter/i));

    await waitFor(() => {
      expect(
        screen.getByText(/email ou mot de passe incorrect/i)
      ).toBeInTheDocument();
    });
  });

  test('redirige vers le dashboard après une connexion réussie', async () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate')
      .mockImplementation(() => mockNavigate);

    renderSignIn();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/mot de passe/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByText(/se connecter/i));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', expect.any(Object));
    });
  });

  test('désactive le formulaire pendant la soumission', async () => {
    renderSignIn();

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/mot de passe/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByText(/se connecter/i));

    await waitFor(() => {
      expect(screen.getByLabelText(/email/i)).toBeDisabled();
      expect(screen.getByLabelText(/mot de passe/i)).toBeDisabled();
      expect(screen.getByText(/se connecter/i)).toBeDisabled();
    });
  });
}); 