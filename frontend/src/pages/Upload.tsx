import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { FileUpload } from "@/components/FileUpload"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload as UploadIcon, FileText, CheckCircle, AlertTriangle } from "lucide-react"

export default function Upload() {
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

  const getUploadStatus = () => {
    const feedbackValid = feedbackFile && !feedbackError
    const demographicsValid = demographicsFile && !demographicsError
    
    if (feedbackValid && demographicsValid) {
      return { status: "complete", message: "Both files uploaded successfully", icon: CheckCircle, color: "text-accent" }
    } else if (feedbackFile || demographicsFile) {
      return { status: "partial", message: "Upload in progress", icon: UploadIcon, color: "text-primary" }
    } else {
      return { status: "pending", message: "No files uploaded", icon: AlertTriangle, color: "text-muted-foreground" }
    }
  }

  const status = getUploadStatus()

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Data Upload</h1>
        <p className="text-muted-foreground">
          Upload your student feedback and demographics data to begin analysis
        </p>
      </div>

      {/* Upload Status */}
      <Card className="shadow-card">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <status.icon className={`w-6 h-6 ${status.color}`} />
            <div>
              <p className="font-semibold">{status.message}</p>
              <p className="text-sm text-muted-foreground">
                Upload both required data files to proceed with analysis
              </p>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2 text-sm">
              {feedbackFile && !feedbackError ? (
                <CheckCircle className="w-4 h-4 text-accent" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
              )}
              <span>Student Feedback Data</span>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              {demographicsFile && !demographicsError ? (
                <CheckCircle className="w-4 h-4 text-accent" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-muted-foreground" />
              )}
              <span>Demographics Data</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="feedback" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="feedback" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Student Feedback</span>
          </TabsTrigger>
          <TabsTrigger value="demographics" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Demographics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="feedback" className="space-y-6">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Student Feedback Data Requirements</CardTitle>
              <CardDescription>
                This file should contain student NPS scores, aspect ratings, and feedback comments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert className="mb-4">
                <FileText className="w-4 h-4" />
                <AlertDescription>
                  <strong>Required columns:</strong> student_id, timestamp, course_id, week_number, 
                  nps_score, aspect_1_score, aspect_2_score, aspect_3_score, comments
                </AlertDescription>
              </Alert>
              
              <FileUpload
                title="Upload Student Feedback Data"
                description="CSV or Excel file with student NPS feedback"
                expectedColumns={feedbackColumns}
                onFileUpload={handleFeedbackUpload}
                uploadedFile={feedbackFile}
                validationError={feedbackError}
                previewData={feedbackData}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="demographics" className="space-y-6">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Demographics Data Requirements</CardTitle>
              <CardDescription>
                This file should contain student demographic information for segmentation analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert className="mb-4">
                <FileText className="w-4 h-4" />
                <AlertDescription>
                  <strong>Required columns:</strong> demographic_type, current_grade, attendance_rate
                </AlertDescription>
              </Alert>
              
              <FileUpload
                title="Upload Demographics Data"
                description="CSV or Excel file with student demographics"
                expectedColumns={demographicsColumns}
                onFileUpload={handleDemographicsUpload}
                uploadedFile={demographicsFile}
                validationError={demographicsError}
                previewData={demographicsData}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => window.location.reload()}>
          Clear All Data
        </Button>
        
        <Button
          disabled={!feedbackFile || !demographicsFile || !!feedbackError || !!demographicsError}
          className="gradient-primary shadow-soft transition-smooth hover:shadow-medium"
        >
          <UploadIcon className="w-4 h-4 mr-2" />
          Process Data
        </Button>
      </div>
    </div>
  )
}