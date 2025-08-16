import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EmotionalGauge } from '../components/EmotionalGauge'
import { useEmotionStore } from '../store/emotionStore'

// Mock the store
vi.mock('../store/emotionStore', () => ({
  useEmotionStore: vi.fn()
}))

describe('EmotionalGauge', () => {
  it('displays loading state', () => {
    // Mock the store values
    vi.mocked(useEmotionStore).mockReturnValue({
      currentStudentEmotion: null,
      isLoading: true,
      error: null,
      fetchStudentEmotions: vi.fn()
    })

    render(<EmotionalGauge studentId="test-123" />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('displays error state', () => {
    // Mock the store values with error
    vi.mocked(useEmotionStore).mockReturnValue({
      currentStudentEmotion: null,
      isLoading: false,
      error: 'Failed to fetch data',
      fetchStudentEmotions: vi.fn()
    })

    render(<EmotionalGauge studentId="test-123" />)
    expect(screen.getByText('Error: Failed to fetch data')).toBeInTheDocument()
  })

  it('displays emotion data correctly', () => {
    // Mock the store values with data
    vi.mocked(useEmotionStore).mockReturnValue({
      currentStudentEmotion: {
        emotionProfile: {
          emotionalComplexity: 'simple',
          frustrationLevel: 0.5,
          hiddenDissatisfaction: {
            flag: true,
            confidence: 0.8
          }
        }
      } as any,
      isLoading: false,
      error: null,
      fetchStudentEmotions: vi.fn()
    })

    render(<EmotionalGauge studentId="test-123" />)
    expect(screen.getByText('Complexity:')).toBeInTheDocument()
    expect(screen.getByText('simple')).toBeInTheDocument()
    expect(screen.getByText('Hidden Dissatisfaction Detected!')).toBeInTheDocument()
  })
})
