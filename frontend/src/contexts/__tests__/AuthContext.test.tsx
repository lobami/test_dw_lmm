import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import { AuthProvider, useAuth } from '../AuthContext'
import api from '../../api/client'

vi.mock('../../api/client')

const MockedApi = api as unknown as { post: jest.Mock }

const TestComponent: React.FC = () => {
  const { user, logout, login } = useAuth()

  return (
    <div>
      <div data-testid="user">{user ? user.email : 'no-user'}</div>
      <button onClick={() => logout()} data-testid="logout">logout</button>
    </div>
  )
}

describe('AuthContext logout', () => {
  beforeEach(() => {
    // clear localStorage
    localStorage.clear()
    ;(MockedApi as any).post = vi.fn().mockResolvedValue({ data: { ok: true } })
  })

  it('calls backend logout and clears access_token', async () => {
    // set a token in localStorage to simulate logged state
    localStorage.setItem('access_token', 'tok')

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    // user should initially be no-user (AuthProvider tries to fetch me on mount conditionally), we simulate logout flow
    const btn = screen.getByTestId('logout')
    fireEvent.click(btn)

    await waitFor(() => {
      expect((MockedApi as any).post).toHaveBeenCalledWith('/auth/logout')
      expect(localStorage.getItem('access_token')).toBeNull()
    })
  })
})
