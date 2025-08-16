import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Calendar, Download, TrendingUp, TrendingDown, Minus } from "lucide-react"

export default function WeeklyReports() {
  const [selectedWeek, setSelectedWeek] = useState("")
  const [selectedCourse, setSelectedCourse] = useState("")

  const weeks = [
    { value: "week-1", label: "Week 1 - Introduction" },
    { value: "week-2", label: "Week 2 - Foundations" },
    { value: "week-3", label: "Week 3 - Core Concepts" },
    { value: "week-4", label: "Week 4 - Advanced Topics" },
  ]

  const courses = [
    { value: "cs101", label: "Computer Science 101" },
    { value: "math201", label: "Mathematics 201" },
    { value: "phys301", label: "Physics 301" },
  ]

  const mockReports = [
    {
      id: 1,
      week: "Week 3",
      course: "Computer Science 101",
      npsScore: 42,
      trend: "up",
      studentsCount: 156,
      responseRate: 87,
      generatedAt: "2024-01-15",
    },
    {
      id: 2,
      week: "Week 2",
      course: "Computer Science 101",
      npsScore: 38,
      trend: "down",
      studentsCount: 160,
      responseRate: 92,
      generatedAt: "2024-01-08",
    },
    {
      id: 3,
      week: "Week 1",
      course: "Computer Science 101",
      npsScore: 45,
      trend: "neutral",
      studentsCount: 162,
      responseRate: 89,
      generatedAt: "2024-01-01",
    },
  ]

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="w-4 h-4 text-accent" />
      case "down":
        return <TrendingDown className="w-4 h-4 text-destructive" />
      default:
        return <Minus className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "up":
        return "text-accent"
      case "down":
        return "text-destructive"
      default:
        return "text-muted-foreground"
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Weekly Reports</h1>
        <p className="text-muted-foreground">
          View and download weekly NPS analysis reports by course and time period
        </p>
      </div>

      {/* Filters */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="text-lg">Report Filters</CardTitle>
          <CardDescription>
            Filter reports by course and week to find specific analysis data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Course</label>
              <Select value={selectedCourse} onValueChange={setSelectedCourse}>
                <SelectTrigger>
                  <SelectValue placeholder="Select course" />
                </SelectTrigger>
                <SelectContent>
                  {courses.map((course) => (
                    <SelectItem key={course.value} value={course.value}>
                      {course.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Week</label>
              <Select value={selectedWeek} onValueChange={setSelectedWeek}>
                <SelectTrigger>
                  <SelectValue placeholder="Select week" />
                </SelectTrigger>
                <SelectContent>
                  {weeks.map((week) => (
                    <SelectItem key={week.value} value={week.value}>
                      {week.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end">
              <Button className="w-full gradient-primary shadow-soft transition-smooth hover:shadow-medium">
                Apply Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reports List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Generated Reports</h2>
          <Badge variant="secondary" className="px-3 py-1">
            {mockReports.length} reports found
          </Badge>
        </div>

        <div className="grid gap-4">
          {mockReports.map((report) => (
            <Card key={report.id} className="gradient-card shadow-card hover:shadow-medium transition-smooth">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-6">
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-5 h-5 text-primary" />
                      <div>
                        <p className="font-semibold">{report.week}</p>
                        <p className="text-sm text-muted-foreground">{report.course}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${getTrendColor(report.trend)}`}>
                          {report.npsScore}
                        </div>
                        <p className="text-xs text-muted-foreground">NPS Score</p>
                      </div>
                      {getTrendIcon(report.trend)}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Students</p>
                        <p className="font-medium">{report.studentsCount}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Response Rate</p>
                        <p className="font-medium">{report.responseRate}%</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="text-right text-sm text-muted-foreground">
                      Generated: {report.generatedAt}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="transition-fast hover:bg-primary hover:text-white"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Promoters:</span>
                      <span className="text-accent font-medium">45%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Passives:</span>
                      <span className="text-muted-foreground font-medium">32%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Detractors:</span>
                      <span className="text-destructive font-medium">23%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}