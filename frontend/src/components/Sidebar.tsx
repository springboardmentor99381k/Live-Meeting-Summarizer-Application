import { Mic, Upload, Users, FileText, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
}

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "recording", label: "Live Recording", icon: Mic },
  { id: "upload", label: "Upload File", icon: Upload },
  { id: "diarization", label: "Diarization", icon: Users },
  { id: "summary", label: "Summary", icon: FileText },
];

const Sidebar = ({ activeModule, onModuleChange }: SidebarProps) => {
  return (
    <aside className="w-64 min-h-screen bg-dark-spruce/50 border-r border-border flex flex-col">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg gradient-camel flex items-center justify-center">
            <Mic className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-heading font-bold text-foreground">MeetMind</h1>
            <span className="text-xs text-camel font-medium tracking-wider uppercase">AI</span>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeModule === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onModuleChange(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-camel/15 text-camel glow-camel"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
              )}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="p-4 m-3 rounded-lg glass-card">
        <p className="text-xs text-muted-foreground">Free Plan</p>
        <p className="text-sm font-medium text-foreground mt-1">3 / 10 meetings</p>
        <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
          <div className="h-full w-[30%] rounded-full gradient-camel" />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
