import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddressForm } from '../../src/components/AddressForm';

describe('AddressForm', () => {
  it('should render address input field and submit button', () => {
    const mockOnSubmit = vi.fn();
    render(<AddressForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/enter your address/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /find my representatives/i })).toBeInTheDocument();
  });

  it('should call onSubmit with address data when form is submitted with valid address', async () => {
    const mockOnSubmit = vi.fn();
    const user = userEvent.setup();
    
    render(<AddressForm onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/enter your address/i);
    const button = screen.getByRole('button', { name: /find my representatives/i });

    await user.type(input, '123 Main St, Seattle, WA 98101');
    await user.click(button);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    expect(mockOnSubmit.mock.calls[0][0]).toEqual({
      address: '123 Main St, Seattle, WA 98101',
    });
  });

  it('should show validation error when address is empty on submit', async () => {
    const mockOnSubmit = vi.fn();
    const user = userEvent.setup();
    
    render(<AddressForm onSubmit={mockOnSubmit} />);

    const button = screen.getByRole('button', { name: /find my representatives/i });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText(/address is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should show validation error when address exceeds 200 characters', async () => {
    const mockOnSubmit = vi.fn();
    const user = userEvent.setup();
    
    render(<AddressForm onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/enter your address/i);
    const longAddress = 'A'.repeat(201);

    await user.type(input, longAddress);
    await user.tab(); // Trigger blur validation

    await waitFor(() => {
      expect(screen.getByText(/address must be under 200 characters/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('should disable form fields when disabled prop is true', () => {
    const mockOnSubmit = vi.fn();
    
    render(<AddressForm onSubmit={mockOnSubmit} disabled={true} />);

    const input = screen.getByLabelText(/enter your address/i);
    const button = screen.getByRole('button', { name: /find my representatives/i });

    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });

  it('should trim whitespace from address before validation', async () => {
    const mockOnSubmit = vi.fn();
    const user = userEvent.setup();
    
    render(<AddressForm onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/enter your address/i);
    const button = screen.getByRole('button', { name: /find my representatives/i });

    await user.type(input, '  123 Main St  ');
    await user.click(button);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    expect(mockOnSubmit.mock.calls[0][0]).toEqual({
      address: '123 Main St',
    });
  });
});
