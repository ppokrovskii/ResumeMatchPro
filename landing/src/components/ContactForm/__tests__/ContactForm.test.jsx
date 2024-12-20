import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ContactForm from '../ContactForm';

describe('ContactForm Modal', () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('submits data in correct format', async () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    await userEvent.type(screen.getByLabelText(/first name/i), 'Pavel');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Pokrovskii');
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/phone/i), '+971581234567');

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith({
        email: 'test@example.com',
        phone: '+971581234567',
        first_name: 'Pavel',
        last_name: 'Pokrovskii'
      });
    });
  });

  it('validates required fields before submission', async () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(await screen.findByText(/first name is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/last name is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it('validates email format', async () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    await userEvent.type(screen.getByLabelText(/email/i), 'invalid-email');
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(await screen.findByText(/invalid email address/i)).toBeInTheDocument();
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it('validates phone number format', async () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    await userEvent.type(screen.getByLabelText(/phone/i), '123');
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(await screen.findByText(/invalid phone number/i)).toBeInTheDocument();
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it('closes modal when close button is clicked', () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    fireEvent.click(screen.getByRole('button', { name: /close form/i }));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('clears form after successful submission', async () => {
    render(
      <ContactForm isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );

    await userEvent.type(screen.getByLabelText(/first name/i), 'Pavel');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Pokrovskii');
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/phone/i), '+971581234567');

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => expect(screen.getByLabelText(/first name/i)).toHaveValue(''));
    await waitFor(() => expect(screen.getByLabelText(/last name/i)).toHaveValue(''));
    await waitFor(() => expect(screen.getByLabelText(/email/i)).toHaveValue(''));
    await waitFor(() => expect(screen.getByLabelText(/phone/i)).toHaveValue(''));
  });
}); 