import '@testing-library/jest-dom'
import { server } from './__tests__/mocks/server'

// Établir le mock de l'API avant tous les tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

// Réinitialiser les handlers entre les tests
afterEach(() => server.resetHandlers())

// Nettoyer après tous les tests
afterAll(() => server.close())
