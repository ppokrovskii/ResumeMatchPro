import { renderHook, act } from '@testing-library/react';
import { useContactForm } from '../useContactForm';
import { submitContactDetails } from '../../services/contactService';

jest.mock('../../services/contactService');

describe('useContactForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('submits contact details in correct format', async () => {
    submitContactDetails.mockResolvedValueOnce({ ok: true });
    const { result } = renderHook(() => useContactForm());

    const contactData = {
      email: 'test@example.com',
      phone: '+971581234567',
      first_name: 'Pavel',
      last_name: 'Pokrovskii'
    };

    await act(async () => {
      await result.current.handleSuccessSubmitContactDetails(contactData);
    });

    expect(submitContactDetails).toHaveBeenCalledWith(contactData);
    expect(result.current.notificationMessage).toBe('Contact details submitted successfully!');
  });

  it('handles submission failure', async () => {
    submitContactDetails.mockRejectedValueOnce(new Error('API Error'));
    const { result } = renderHook(() => useContactForm());

    await act(async () => {
      await result.current.handleSuccessSubmitContactDetails({});
    });

    expect(result.current.notificationMessage).toBe('An error occurred while submitting contact details.');
  });

  it('handles non-ok response', async () => {
    submitContactDetails.mockResolvedValueOnce({ ok: false });
    const { result } = renderHook(() => useContactForm());

    await act(async () => {
      await result.current.handleSuccessSubmitContactDetails({});
    });

    expect(result.current.notificationMessage).toBe('Failed to submit contact details.');
  });

  it('closes form after submission', async () => {
    submitContactDetails.mockResolvedValueOnce({ ok: true });
    const { result } = renderHook(() => useContactForm());

    await act(async () => {
      result.current.handleOpenContactForm();
    });
    expect(result.current.isContactFormOpen).toBe(true);

    await act(async () => {
      await result.current.handleSuccessSubmitContactDetails({});
    });
    expect(result.current.isContactFormOpen).toBe(false);
  });

  it('clears notification message', async () => {
    const { result } = renderHook(() => useContactForm());

    await act(async () => {
      result.current.handleNotificationClose();
    });

    expect(result.current.notificationMessage).toBe('');
  });
}); 