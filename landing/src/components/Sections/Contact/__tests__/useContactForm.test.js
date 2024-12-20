import { renderHook, act } from '@testing-library/react';
import { useContactForm } from '../useContactForm';
import { submitContactDetails } from '../../../../services/contactService';

jest.mock('../../../../services/contactService');

describe('useContactForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with empty form state', () => {
    const { result } = renderHook(() => useContactForm());

    expect(result.current.formState).toEqual({
      firstName: '',
      lastName: '',
      email: '',
      phone: ''
    });
    expect(result.current.isSubmitting).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.success).toBe(false);
  });

  it('updates form fields correctly', () => {
    const { result } = renderHook(() => useContactForm());

    act(() => {
      result.current.handleChange('firstName', 'John');
    });

    expect(result.current.formState.firstName).toBe('John');
  });

  it('handles successful form submission', async () => {
    submitContactDetails.mockResolvedValueOnce({ ok: true });
    const { result } = renderHook(() => useContactForm());

    // Prepare form data
    act(() => {
      result.current.handleChange('firstName', 'John');
      result.current.handleChange('lastName', 'Doe');
      result.current.handleChange('email', 'john@example.com');
      result.current.handleChange('phone', '1234567890');
    });

    // Submit form
    await act(async () => {
      await result.current.handleSubmit({ preventDefault: jest.fn() });
    });

    expect(submitContactDetails).toHaveBeenCalledWith({
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      phone: '1234567890'
    });

    expect(result.current.success).toBe(true);
    expect(result.current.error).toBeNull();
    expect(result.current.formState).toEqual({
      firstName: '',
      lastName: '',
      email: '',
      phone: ''
    });
  });

  it('handles submission failure', async () => {
    submitContactDetails.mockRejectedValueOnce(new Error('API Error'));
    const { result } = renderHook(() => useContactForm());

    await act(async () => {
      await result.current.handleSubmit({ preventDefault: jest.fn() });
    });

    expect(result.current.error).toBe('An error occurred while submitting contact details.');
    expect(result.current.success).toBe(false);
  });
}); 