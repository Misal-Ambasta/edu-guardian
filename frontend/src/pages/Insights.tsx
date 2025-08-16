import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Users, TrendingDown, AlertTriangle, MessageSquare, GraduationCap } from "lucide-react"

export default function Insights() {
  const atRiskStudents = [
    {
      id: "STU001",
      name: "Alex Johnson",
      course: "Computer Science 101",
      riskLevel: "High",
      npsScore: 2,
      attendance: 65,
      lastFeedback: "Course moving too fast, struggling with concepts",
      week: 3,
    },
    {
      id: "STU015",
      name: "Sarah Chen",
      course: "Computer Science 101",
      riskLevel: "Medium",
      npsScore: 4,
      attendance: 78,
      lastFeedback: "Need more practice exercises",
      week: 3,
    },
    {
      id: "STU032",
      name: "Michael Brown",
      course: "Computer Science 101",
      riskLevel: "High",
      npsScore: 1,
      attendance: 45,
      lastFeedback: "Very confused, considering dropping",
      week: 2,
    },
  ]

  const segments = [
    {
      name: "High Achievers",
      count: 45,
      percentage: 28,
      avgNps: 8.2,
      icon: GraduationCap,
      color: "text-accent",
      description: "Students consistently performing well with high satisfaction",
    },
    {
      name: "Average Performers",
      count: 89,
      percentage: 56,
      avgNps: 6.1,
      icon: Users,
      color: "text-primary",
      description: "Students with moderate performance and satisfaction levels",
    },
    {
      name: "At-Risk Students",
      count: 26,
      percentage: 16,
      avgNps: 3.4,
      icon: AlertTriangle,
      color: "text-destructive",
      description: "Students showing signs of disengagement or poor performance",
    },
  ]

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case "High":
        return "bg-destructive text-white"
      case "Medium":
        return "bg-orange-500 text-white"
      default:
        return "bg-muted"
    }
  }

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Student Insights</h1>
        <p className="text-muted-foreground">
          Detailed analysis of student segments and individual risk assessments
        </p>
      </div>

      {/* Student Segmentation */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Student Segmentation</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {segments.map((segment, index) => (
            <Card key={index} className="gradient-card shadow-card">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{segment.name}</CardTitle>
                  <segment.icon className={`w-5 h-5 ${segment.color}`} />
                </div>
                <CardDescription>{segment.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold">{segment.count}</span>
                    <span className="text-sm text-muted-foreground">{segment.percentage}%</span>
                  </div>
                  
                  <Progress value={segment.percentage} className="h-2" />
                  
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Avg NPS Score:</span>
                    <span className={`font-medium ${segment.color}`}>{segment.avgNps}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* At-Risk Students */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">At-Risk Students</h2>
          <Badge variant="destructive" className="px-3 py-1">
            {atRiskStudents.length} students need attention
          </Badge>
        </div>

        <div className="space-y-4">
          {atRiskStudents.map((student) => (
            <Card key={student.id} className="shadow-card hover:shadow-medium transition-smooth">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center space-x-3">
                      <div>
                        <h3 className="font-semibold">{student.name}</h3>
                        <p className="text-sm text-muted-foreground">ID: {student.id}</p>
                      </div>
                      <Badge className={getRiskBadgeColor(student.riskLevel)}>
                        {student.riskLevel} Risk
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Course</p>
                        <p className="font-medium">{student.course}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">NPS Score</p>
                        <p className={`font-medium ${student.npsScore <= 3 ? 'text-destructive' : 'text-primary'}`}>
                          {student.npsScore}/10
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Attendance</p>
                        <p className={`font-medium ${student.attendance < 70 ? 'text-destructive' : 'text-accent'}`}>
                          {student.attendance}%
                        </p>
                      </div>
                    </div>
                    
                    <div className="bg-muted/50 p-3 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <MessageSquare className="w-4 h-4 text-muted-foreground mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-medium">Latest Feedback (Week {student.week})</p>
                          <p className="text-sm text-muted-foreground mt-1">"{student.lastFeedback}"</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ml-6">
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Action Recommendations */}
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Recommended Actions</CardTitle>
          <CardDescription>
            AI-generated recommendations based on current student data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-3 p-3 bg-destructive/5 rounded-lg border border-destructive/20">
              <AlertTriangle className="w-5 h-5 text-destructive mt-1" />
              <div>
                <p className="font-medium text-destructive">Immediate Attention Required</p>
                <p className="text-sm text-muted-foreground mt-1">
                  3 students showing critical risk factors. Consider individual meetings or additional support.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-primary/5 rounded-lg border border-primary/20">
              <TrendingDown className="w-5 h-5 text-primary mt-1" />
              <div>
                <p className="font-medium text-primary">Course Pace Review</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Multiple students report course moving too fast. Consider reviewing pacing for weeks 3-4.
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-accent/5 rounded-lg border border-accent/20">
              <Users className="w-5 h-5 text-accent mt-1" />
              <div>
                <p className="font-medium text-accent">Peer Support Program</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Pair high-achieving students with at-risk students for additional support.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}