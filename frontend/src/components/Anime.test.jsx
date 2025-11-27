// src/components/Anime.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Anime from './Anime';

describe('Anime component', () => {
  test('renders the input area', () => {
    render(<Anime />);

    // Grab the first textbox (your input field)
    const inputs = screen.getAllByRole('textbox');
    expect(inputs.length).toBeGreaterThan(0);
  });

  test('updates input text when user types', async () => {
    const user = userEvent.setup();
    render(<Anime />);

    const inputs = screen.getAllByRole('textbox');
    const questionInput = inputs[0];

    await user.type(questionInput, 'Recommend me an anime');

    expect(questionInput).toHaveValue('Recommend me an anime');
  });
});
