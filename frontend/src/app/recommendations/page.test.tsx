import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import RecommendationsPage from './page'
import * as authContext from '@/lib/auth-context'
import * as api from '@/lib/api'
import { Role } from '@/lib/types'

// Mock the AuthContext
vi.mock('@/lib/auth-context', () => ({
  useAuth: vi.fn(),
}))

// Mock API calls
vi.mock('@/lib/api', () => ({
  apiGet: vi.fn(),
  describeApiError: vi.fn(),
}))

describe('RecommendationsPage', () => {
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

  it('renders loading state initially', () => {
    vi.mocked(api.apiGet).mockImplementation(() => new Promise(() => {}))
    render(<RecommendationsPage />)
    expect(screen.getByText('Loading recommendations...')).toBeDefined()
  })

  it('renders empty state when no recommendations', async () => {
    vi.mocked(api.apiGet).mockResolvedValue({ data: [], pagination: { page: 1, pageSize: 20, totalItems: 0, totalPages: 0 } })
    
    render(<RecommendationsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('No recommendations found')).toBeDefined()
    })
  })

  it('renders recommendations successfully', async () => {
    vi.mocked(api.apiGet).mockImplementation(async (path) => {
      if (path === '/recommendations') {
        return {
          data: [
            {
              id: 'rec-1',
              periodDate: '2026-10-10',
              locationId: 'loc-1',
              mealTypeId: 'meal-1',
              estimatedSurplusQuantity: 50,
              recommendationText: 'Transfer 50 to North Campus',
              isAdvisory: true,
            }
          ],
          pagination: { page: 1, pageSize: 20, totalItems: 1, totalPages: 1 }
        }
      }
      if (path === '/locations') return { data: [{ id: 'loc-1', name: 'Main Cafe' }] }
      if (path === '/meal-types') return { data: [{ id: 'meal-1', name: 'Lunch' }] }
      return { data: [] }
    })

    render(<RecommendationsPage />)

    await waitFor(() => {
      expect(screen.getByText('Main Cafe')).toBeDefined()
      expect(screen.getByText('Lunch')).toBeDefined()
      expect(screen.getByText('Transfer 50 to North Campus')).toBeDefined()
      expect(screen.getByText('Advisory Only')).toBeDefined()
    })
  })
})
