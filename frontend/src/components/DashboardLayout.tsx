import { ReactNode } from "react"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "./AppSidebar"

interface DashboardLayoutProps {
  children: ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full gradient-subtle">
        <AppSidebar />
        
        <div className="flex-1 flex flex-col">
          <header className="h-14 flex items-center border-b bg-card shadow-soft px-4">
            <SidebarTrigger className="transition-fast" />
            <div className="ml-4">
              <h1 className="text-lg font-semibold text-foreground">NPS Intelligence Platform</h1>
            </div>
          </header>
          
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}