import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Contact from '../Contact';
import { submitContactDetails } from '../../../../services/contactService';

// Mock the service
jest.mock('../../../../services/contactService');

describe('Contact Component', () => {
  const mockHandleOpenContactForm = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders contact form with all fields', async () => {
    render(<Contact handleOpenContactForm={mockHandleOpenContactForm} />);
    
    await screen.findByLabelText(/first name/i);
    await screen.findByLabelText(/last name/i);
    await screen.findByLabelText(/email/i);
    await screen.findByLabelText(/phone number/i);
  });

  it('submits form data correctly without opening ContactForm modal', async () => {
    submitContactDetails.mockResolvedValueOnce({ ok: true });

    render(<Contact handleOpenContactForm={mockHandleOpenContactForm} />);

    await userEvent.type(screen.getByLabelText(/first name/i), 'John');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Doe');
    await userEvent.type(screen.getByLabelText(/email/i), 'john@example.com');
    await userEvent.type(screen.getByLabelText(/phone/i), '1234567890');

    fireEvent.click(screen.getByRole('button', { name: /get early access/i }));

    await waitFor(() => {
      expect(submitContactDetails).toHaveBeenCalledWith({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '1234567890'
      });
    });

    expect(mockHandleOpenContactForm).not.toHaveBeenCalled();

    await screen.findByText(/contact details submitted successfully/i);
  });

  it('shows error message on submission failure', async () => {
    submitContactDetails.mockRejectedValueOnce(new Error('API Error'));

    render(<Contact handleOpenContactForm={mockHandleOpenContactForm} />);

    await userEvent.type(screen.getByLabelText(/first name/i), 'John');
    await userEvent.type(screen.getByLabelText(/last name/i), 'Doe');
    await userEvent.type(screen.getByLabelText(/email/i), 'john@example.com');
    await userEvent.type(screen.getByLabelText(/phone/i), '1234567890');

    fireEvent.click(screen.getByRole('button', { name: /get early access/i }));

    await screen.findByText(/an error occurred/i);

    expect(mockHandleOpenContactForm).not.toHaveBeenCalled();
  });

  it('validates required fields', async () => {
    render(<Contact handleOpenContactForm={mockHandleOpenContactForm} />);

    const form = screen.getByTestId('contact-form');
    const submitButton = screen.getByRole('button', { name: /get early access/i });
    
    // Check form validity before submission
    expect(form.checkValidity()).toBe(false);
    expect(submitButton).not.toBeDisabled();

    await waitFor(() => expect(screen.getByLabelText(/first name/i)).toBeInvalid());
    await waitFor(() => expect(screen.getByLabelText(/last name/i)).toBeInvalid());
    await waitFor(() => expect(screen.getByLabelText(/email/i)).toBeInvalid());
    await waitFor(() => expect(screen.getByLabelText(/phone/i)).not.toBeInvalid());

    expect(submitContactDetails).not.toHaveBeenCalled();
  });
}); 