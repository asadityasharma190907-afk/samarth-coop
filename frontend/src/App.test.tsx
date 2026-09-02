import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );
    // Smoke test to ensure it renders something
    expect(document.body).toBeInTheDocument();
  });
});
