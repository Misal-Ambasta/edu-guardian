import { Link } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Brain, BarChart3, Upload, Users, TrendingUp, CheckCircle } from "lucide-react"

const Index = () => {
  const features = [
    {
      icon: Upload,
      title: "Easy Data Upload",
      description: "Drag-and-drop CSV/Excel files with automatic validation"
    },
    {
      icon: BarChart3,
      title: "NPS Analytics",
      description: "Comprehensive NPS scoring and trend analysis"
    },
    {
      icon: Users,
      title: "Student Segmentation",
      description: "Identify at-risk students and performance patterns"
    },
    {
      icon: TrendingUp,
      title: "Weekly Reports",
      description: "Automated reporting with actionable insights"
    }
  ]

  return (
    <div className="min-h-screen gradient-subtle">
      {/* Header */}
      <header className="border-b bg-card shadow-soft">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold">NPS Intelligence</h1>
                <p className="text-xs text-muted-foreground">Analytics Platform</p>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link to="/login">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button className="gradient-primary shadow-soft transition-smooth hover:shadow-medium">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="space-y-8">
            <div>
              <h1 className="text-5xl font-bold mb-6">
                Transform Student Feedback into
                <span className="gradient-primary bg-clip-text text-transparent"> Actionable Insights</span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
                Upload your student data, get comprehensive NPS analysis, identify at-risk students, 
                and generate actionable reports to improve educational outcomes.
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <Link to="/register">
                <Button size="lg" className="gradient-primary shadow-medium transition-smooth hover:shadow-soft text-lg px-8 py-3">
                  Start Free Analysis
                </Button>
              </Link>
              <Link to="/login">
                <Button size="lg" variant="outline" className="text-lg px-8 py-3">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 bg-card/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Powerful Analytics Made Simple</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Everything you need to analyze student satisfaction and improve educational outcomes
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="gradient-card shadow-card hover:shadow-medium transition-smooth">
                <CardContent className="p-6 text-center">
                  <feature.icon className="w-12 h-12 text-primary mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <h2 className="text-3xl font-bold">Why Choose NPS Intelligence?</h2>
              <div className="space-y-4">
                {[
                  "Automated data validation and error detection",
                  "AI-powered student segmentation and risk analysis", 
                  "Weekly automated reports with actionable insights",
                  "Real-time dashboard with comprehensive analytics"
                ].map((benefit, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-accent flex-shrink-0" />
                    <span>{benefit}</span>
                  </div>
                ))}
              </div>
              <Link to="/register">
                <Button className="gradient-primary shadow-soft transition-smooth hover:shadow-medium">
                  Get Started Today
                </Button>
              </Link>
            </div>
            <div className="bg-muted/50 rounded-lg p-8 text-center">
              <div className="space-y-4">
                <BarChart3 className="w-24 h-24 text-primary mx-auto" />
                <h3 className="text-xl font-semibold">Ready to Begin?</h3>
                <p className="text-muted-foreground">
                  Join educators who are already using data-driven insights to improve student outcomes.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center space-x-3 text-muted-foreground">
            <Brain className="w-5 h-5" />
            <span>© 2024 NPS Intelligence Platform. Built for educational excellence.</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
