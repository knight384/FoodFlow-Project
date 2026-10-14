import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import ReportsPage from './page'
import * as authContext from '@/lib/auth-context'
import * as api from '@/lib/api'
import { Role } from '@/lib/types'

vi.mock('@/lib/auth-context', () => ({
  useAuth: vi.fn(),
}))

vi.mock('@/lib/api', () => ({
  apiGet: vi.fn(),
  describeApiError: vi.fn(),
}))

describe('ReportsPage', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.mocked(authContext.useAuth).mockReturnValue({
      user: { id: 'u1', username: 'Manager', role: 'manager' as Role },
      token: 'fake-token',
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })
  })

  it('renders initial state prompting search', async () => {
    vi.mocked(api.apiGet).mockImplementation(async (path) => {
      if (path === '/locations') return { data: [] }
      if (path === '/meal-types') return { data: [] }
      return { data: [] }
    })
    
    render(<ReportsPage />)
    expect(screen.getByText('Select a date range and click Search to view reports.')).toBeDefined()
  })

  it('performs search and displays results', async () => {
    vi.mocked(api.apiGet).mockImplementation(async (path) => {
      if (path === '/reports') {
        return {
          data: [
            {
              date: '2026-10-10',
              locationId: 'loc-1',
              mealTypeId: 'meal-1',
              forecastedDemand: 100,
              plannedQuantity: 150,
              variancePercentage: 50,
              potentialSurplus: 50,
              potentialShortage: 0,
              status: 'surplus',
            }
          ],
          pagination: { page: 1, pageSize: 20, totalItems: 1, totalPages: 1 }
        }
      }
      if (path === '/locations') return { data: [{ id: 'loc-1', name: 'Main Cafe' }] }
      if (path === '/meal-types') return { data: [{ id: 'meal-1', name: 'Lunch' }] }
      return { data: [] }
    })

    render(<ReportsPage />)
    
    // Fill form
    fireEvent.change(screen.getByLabelText('From Date'), { target: { value: '2026-10-01' } })
    fireEvent.change(screen.getByLabelText('To Date'), { target: { value: '2026-10-31' } })
    
    // Submit
    await waitFor(() => {
      fireEvent.submit(screen.getByText('Search').closest('form')!)
    })

    expect(await screen.findByText('Main Cafe')).toBeDefined()
    expect(await screen.findByText('Lunch')).toBeDefined()
    
    const surplusElements = await screen.findAllByText('Surplus')
    expect(surplusElements.length).toBeGreaterThanOrEqual(1)
  })
})
