module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/src/__mocks__/fileMock.js',
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
    }],
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/src/types/',
    '/src/__mocks__/',
    '/src/setupTests.ts',
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/build/',
  ],
  globals: {
    'ts-jest': {
      isolatedModules: true,
    },
  },
  moduleDirectories: ['node_modules', 'src'],
}; 