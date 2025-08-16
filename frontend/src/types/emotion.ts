export interface EmotionProfile {
  emotionalComplexity: 'simple' | 'mixed' | 'complex' | 'conflicted';
  frustrationLevel: number;
  frustrationType: string;
  urgencyLevel: 'low' | 'medium' | 'high';
  emotionalTemperature: number;
  hiddenDissatisfaction: {
    flag: boolean;
    confidence: number;
  };
}

export interface StudentEmotion {
  studentId: string;
  timestamp: string;
  courseId: string;
  weekNumber: number;
  npsScore: number;
  emotionProfile: EmotionProfile;
  currentGrade: number;
  attendanceRate: number;
  completionStatus: string;
  jobPlacement: string;
}

export interface WeeklyReport {
  weekNumber: number;
  courseName: string;
  batchId: string;
  reportDate: string;
  npsScore: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  riskLevel: 'low' | 'medium' | 'high';
  hiddenDissatisfactionRate: number;
  criticalCount: number;
  predictionSummary: string;
  criticalAlerts: string[];
  topInsights: string[];
  prioritizedActions: string[];
}

export interface EmotionalTrend {
  weekNumber: number;
  frustrationLevel: number;
  hiddenDissatisfactionRate: number;
  emotionalTemperature: number;
  engagementLevel: number;
  timestamp: string;
}
