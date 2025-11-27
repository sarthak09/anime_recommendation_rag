// src/App.test.jsx
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  test('renders Anime component via App', () => {
    render(<App />);

    // We know Anime has a Reset button (from your code)
    // This also proves App successfully renders Anime.
    const resetButton = screen.getByRole('button', { name: /reset/i });
    expect(resetButton).toBeInTheDocument();
  });
});
