import api from './api';
import type { EmotionProfile, StudentEmotion, WeeklyReport, EmotionalTrend } from '../types/emotion';

export const EmotionService = {
  async getStudentEmotions(studentId: string): Promise<StudentEmotion[]> {
    const { data } = await api.get(`/students/${studentId}/emotions`);
    return data;
  },

  async getWeeklyReport(courseId: string, weekNumber: number): Promise<WeeklyReport> {
    const { data } = await api.get(`/courses/${courseId}/reports/week/${weekNumber}`);
    return data;
  },

  async updateEmotionProfile(
    studentId: string,
    emotionProfile: EmotionProfile
  ): Promise<StudentEmotion> {
    const { data } = await api.put(`/students/${studentId}/emotion-profile`, emotionProfile);
    return data;
  },

  async getEmotionalTrends(courseId: string): Promise<EmotionalTrend[]> {
    const { data } = await api.get(`/courses/${courseId}/emotional-trends`);
    return data;
  },

  async getHiddenDissatisfactionAlerts(): Promise<any> {
    const { data } = await api.get('/alerts/hidden-dissatisfaction');
    return data;
  },

  // New methods based on PRD
  async predictEmotionTrajectory(studentId: string): Promise<any> {
    const { data } = await api.get(`/students/${studentId}/emotion-trajectory-prediction`);
    return data;
  },

  async getInterventionRecommendations(studentId: string): Promise<any> {
    const { data } = await api.get(`/students/${studentId}/emotion-intervention-recommend`);
    return data;
  },

  async getFrustrationAnalysis(courseId: string): Promise<any> {
    const { data } = await api.get(`/emotions/frustration-analysis/${courseId}`);
    return data;
  },

  async getUrgencyDistribution(courseId: string): Promise<any> {
    const { data } = await api.get(`/emotions/urgency-distribution/${courseId}`);
    return data;
  },

  async predictEmotionalCrisis(studentData: any): Promise<any> {
    const { data } = await api.post('/emotions/emotional-crisis-prediction', studentData);
    return data;
  },

  async applyEmotionalIntervention(interventionData: any): Promise<any> {
    const { data } = await api.post('/interventions/emotion-targeted', interventionData);
    return data;
  },

  async getInterventionSuccessRates(): Promise<any> {
    const { data } = await api.get('/interventions/emotion-success-rates');
    return data;
  },

  async generateEmotionReport(courseId: string): Promise<any> {
    const { data } = await api.post('/reports/generate-emotion-report', { courseId });
    return data;
  },

  async getEmotionReportHistory(courseId: string): Promise<any> {
    const { data } = await api.get(`/reports/emotion-report-history/${courseId}`);
    return data;
  }
};
