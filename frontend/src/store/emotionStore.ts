import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { EmotionProfile, StudentEmotion, WeeklyReport } from '../types/emotion';
import { EmotionService } from '../services/EmotionService';

interface EmotionState {
  // State
  currentStudentEmotion: StudentEmotion | null;
  weeklyReport: WeeklyReport | null;
  emotionalTrends: any[];
  emotionTrajectory: any;
  interventionRecommendations: any[];
  frustrationAnalysis: any;
  urgencyDistribution: any;
  crisisPrediction: any;
  interventionResults: any[];
  interventionSuccessRates: any;
  reportHistory: any[];
  isLoading: boolean;
  error: string | null;
  
  // Basic Actions
  fetchStudentEmotions: (studentId: string) => Promise<void>;
  fetchWeeklyReport: (courseId: string, weekNumber: number) => Promise<void>;
  updateEmotionProfile: (studentId: string, profile: EmotionProfile) => Promise<void>;
  fetchEmotionalTrends: (courseId: string) => Promise<void>;
  
  // Advanced Emotion Analysis Actions
  predictEmotionTrajectory: (studentId: string) => Promise<void>;
  getInterventionRecommendations: (studentId: string) => Promise<void>;
  getFrustrationAnalysis: (courseId: string) => Promise<void>;
  getUrgencyDistribution: (courseId: string) => Promise<void>;
  predictEmotionalCrisis: (studentData: any) => Promise<void>;
  
  // Intervention Actions
  applyEmotionalIntervention: (interventionData: any) => Promise<void>;
  getInterventionSuccessRates: () => Promise<void>;
  
  // Report Actions
  generateEmotionReport: (courseId: string) => Promise<void>;
  getEmotionReportHistory: (courseId: string) => Promise<void>;
  
  // Utility Actions
  resetError: () => void;
}

export const useEmotionStore = create<EmotionState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentStudentEmotion: null,
      weeklyReport: null,
      emotionalTrends: [],
      emotionTrajectory: null,
      interventionRecommendations: [],
      frustrationAnalysis: null,
      urgencyDistribution: null,
      crisisPrediction: null,
      interventionResults: [],
      interventionSuccessRates: null,
      reportHistory: [],
      isLoading: false,
      error: null,

      // Basic actions
      fetchStudentEmotions: async (studentId: string) => {
        set({ isLoading: true, error: null });
        try {
          const emotions = await EmotionService.getStudentEmotions(studentId);
          set({ currentStudentEmotion: emotions[0], isLoading: false });
        } catch (error) {
          set({ error: 'Failed to fetch student emotions', isLoading: false });
        }
      },

      fetchWeeklyReport: async (courseId: string, weekNumber: number) => {
        set({ isLoading: true, error: null });
        try {
          const report = await EmotionService.getWeeklyReport(courseId, weekNumber);
          set({ weeklyReport: report, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to fetch weekly report', isLoading: false });
        }
      },

      fetchEmotionalTrends: async (courseId: string) => {
        set({ isLoading: true, error: null });
        try {
          const trends = await EmotionService.getEmotionalTrends(courseId);
          set({ emotionalTrends: trends, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to fetch emotional trends', isLoading: false });
        }
      },

      updateEmotionProfile: async (studentId: string, profile: EmotionProfile) => {
        set({ isLoading: true, error: null });
        try {
          const updatedEmotion = await EmotionService.updateEmotionProfile(studentId, profile);
          set({ currentStudentEmotion: updatedEmotion, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to update emotion profile', isLoading: false });
        }
      },

      // Advanced emotion analysis actions
      predictEmotionTrajectory: async (studentId: string) => {
        set({ isLoading: true, error: null });
        try {
          const trajectory = await EmotionService.predictEmotionTrajectory(studentId);
          set({ emotionTrajectory: trajectory, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to predict emotion trajectory', isLoading: false });
        }
      },

      getInterventionRecommendations: async (studentId: string) => {
        set({ isLoading: true, error: null });
        try {
          const recommendations = await EmotionService.getInterventionRecommendations(studentId);
          set({ interventionRecommendations: recommendations, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to get intervention recommendations', isLoading: false });
        }
      },

      getFrustrationAnalysis: async (courseId: string) => {
        set({ isLoading: true, error: null });
        try {
          const analysis = await EmotionService.getFrustrationAnalysis(courseId);
          set({ frustrationAnalysis: analysis, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to get frustration analysis', isLoading: false });
        }
      },

      getUrgencyDistribution: async (courseId: string) => {
        set({ isLoading: true, error: null });
        try {
          const distribution = await EmotionService.getUrgencyDistribution(courseId);
          set({ urgencyDistribution: distribution, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to get urgency distribution', isLoading: false });
        }
      },

      predictEmotionalCrisis: async (studentData: any) => {
        set({ isLoading: true, error: null });
        try {
          const prediction = await EmotionService.predictEmotionalCrisis(studentData);
          set({ crisisPrediction: prediction, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to predict emotional crisis', isLoading: false });
        }
      },

      // Intervention actions
      applyEmotionalIntervention: async (interventionData: any) => {
        set({ isLoading: true, error: null });
        try {
          const result = await EmotionService.applyEmotionalIntervention(interventionData);
          set({ 
            interventionResults: [...get().interventionResults, result], 
            isLoading: false 
          });
        } catch (error) {
          set({ error: 'Failed to apply intervention', isLoading: false });
        }
      },

      getInterventionSuccessRates: async () => {
        set({ isLoading: true, error: null });
        try {
          const rates = await EmotionService.getInterventionSuccessRates();
          set({ interventionSuccessRates: rates, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to get intervention success rates', isLoading: false });
        }
      },

      // Report actions
      generateEmotionReport: async (courseId: string) => {
        set({ isLoading: true, error: null });
        try {
          const report = await EmotionService.generateEmotionReport(courseId);
          set({ weeklyReport: report, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to generate emotion report', isLoading: false });
        }
      },

      getEmotionReportHistory: async (courseId: string) => {
        set({ isLoading: true, error: null });
        try {
          const history = await EmotionService.getEmotionReportHistory(courseId);
          set({ reportHistory: history, isLoading: false });
        } catch (error) {
          set({ error: 'Failed to get report history', isLoading: false });
        }
      },

      // Utility actions
      resetError: () => set({ error: null }),
    }),
    {
      name: 'emotion-storage',
      partialize: (state) => ({
        currentStudentEmotion: state.currentStudentEmotion,
        weeklyReport: state.weeklyReport,
        emotionalTrends: state.emotionalTrends,
        reportHistory: state.reportHistory,
      }),
    }
  )
);
