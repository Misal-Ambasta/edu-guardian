import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FileUpload } from "@/components/FileUpload"
import { BarChart3, TrendingUp, Users, AlertTriangle } from "lucide-react"

export default function Dashboard() {
  const [feedbackFile, setFeedbackFile] = useState<File | undefined>()
  const [demographicsFile, setDemographicsFile] = useState<File | undefined>()
  const [feedbackData, setFeedbackData] = useState<any[]>([])
  const [demographicsData, setDemographicsData] = useState<any[]>([])
  const [feedbackError, setFeedbackError] = useState("")
  const [demographicsError, setDemographicsError] = useState("")

  const feedbackColumns = [
    "student_id", "timestamp", "course_id", "week_number", 
    "nps_score", "aspect_1_score", "aspect_2_score", "aspect_3_score", "comments"
  ]
  
  const demographicsColumns = [
    "demographic_type", "current_grade", "attendance_rate"
  ]

  const handleFeedbackUpload = (file: File, data: any[]) => {
    if (data.length === 0) {
      setFeedbackError("Invalid file format. Please check column headers match expected format.")
      setFeedbackData([])
    } else {
      setFeedbackError("")
      setFeedbackData(data)
    }
    setFeedbackFile(file)
  }

  const handleDemographicsUpload = (file: File, data: any[]) => {
    if (data.length === 0) {
      setDemographicsError("Invalid file format. Please check column headers match expected format.")
      setDemographicsData([])
    } else {
      setDemographicsError("")
      setDemographicsData(data)
    }
    setDemographicsFile(file)
  }

  const canRunAnalysis = feedbackFile && demographicsFile && !feedbackError && !demographicsError

  const handleRunAnalysis = () => {
    // TODO: Implement actual analysis
    alert("Analysis started! (This is a demo - actual analysis would process the data)")
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Upload your data files to begin NPS analysis</p>
      </div>

      {/* Upload Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FileUpload
          title="Student Feedback Data"
          description="Upload CSV/Excel with student NPS scores and feedback"
          expectedColumns={feedbackColumns}
          onFileUpload={handleFeedbackUpload}
          uploadedFile={feedbackFile}
          validationError={feedbackError}
          previewData={feedbackData}
        />
        
        <FileUpload
          title="Demographics Data"
          description="Upload CSV/Excel with student demographic information"
          expectedColumns={demographicsColumns}
          onFileUpload={handleDemographicsUpload}
          uploadedFile={demographicsFile}
          validationError={demographicsError}
          previewData={demographicsData}
        />
      </div>

      {/* Run Analysis Section */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Control</CardTitle>
          <CardDescription>
            Run the NPS intelligence analysis once both files are uploaded
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">
                Status: {canRunAnalysis ? "Ready to analyze" : "Waiting for valid data files"}
              </p>
              <p className="text-xs text-muted-foreground">
                Both files must be uploaded and validated before analysis can begin
              </p>
            </div>
            <Button
              onClick={handleRunAnalysis}
              disabled={!canRunAnalysis}
              className="gradient-primary shadow-soft transition-smooth hover:shadow-medium"
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Run Analysis
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Section - Placeholder */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="gradient-card shadow-card">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">NPS Summary</CardTitle>
              <TrendingUp className="w-5 h-5 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">--</div>
              <p className="text-sm text-muted-foreground">Overall NPS Score</p>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span>Promoters:</span>
                <span className="text-accent">--%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Passives:</span>
                <span className="text-muted-foreground">--%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Detractors:</span>
                <span className="text-destructive">--%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="gradient-card shadow-card">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Student Segments</CardTitle>
              <Users className="w-5 h-5 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">High Performers</span>
                <span className="text-sm font-medium">--</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Average Performers</span>
                <span className="text-sm font-medium">--</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">At-Risk Students</span>
                <span className="text-sm font-medium text-destructive">--</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="gradient-card shadow-card">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Risk Alerts</CardTitle>
              <AlertTriangle className="w-5 h-5 text-destructive" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-3xl font-bold text-destructive">--</div>
              <p className="text-sm text-muted-foreground">Students at Risk</p>
            </div>
            <Alert className="mt-4">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription className="text-xs">
                Upload data to see risk analysis and alerts
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}