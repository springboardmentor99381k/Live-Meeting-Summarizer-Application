import { motion } from "framer-motion";
import { Mic, Upload, Users, FileText } from "lucide-react";

interface DashboardHomeProps {
  onModuleChange: (module: string) => void;
}

const stats = [
  { label: "Total Meetings", value: "24", change: "+3 this week" },
  { label: "Hours Recorded", value: "18.5h", change: "+2.1h today" },
  { label: "Speakers Identified", value: "47", change: "Across all meetings" },
  { label: "Summaries Generated", value: "22", change: "92% completion" },
];

const quickActions = [
  { id: "recording", label: "Start Live Recording", icon: Mic, desc: "Record a meeting in real-time" },
  { id: "upload", label: "Upload Audio/Video", icon: Upload, desc: "Upload MP3, MP4, or WAV files" },
  { id: "diarization", label: "Speaker Diarization", icon: Users, desc: "Identify who said what" },
  { id: "summary", label: "View Summaries", icon: FileText, desc: "Browse meeting summaries" },
];

const DashboardHome = ({ onModuleChange }: DashboardHomeProps) => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-heading font-bold text-foreground">Welcome back</h2>
        <p className="text-muted-foreground mt-1">Here's an overview of your meeting activity.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card rounded-xl p-5"
          >
            <p className="text-sm text-muted-foreground">{stat.label}</p>
            <p className="text-2xl font-heading font-bold text-foreground mt-1">{stat.value}</p>
            <p className="text-xs text-camel mt-2">{stat.change}</p>
          </motion.div>
        ))}
      </div>

      <div>
        <h3 className="text-lg font-heading font-semibold text-foreground mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action, i) => {
            const Icon = action.icon;
            return (
              <motion.button
                key={action.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                onClick={() => onModuleChange(action.id)}
                className="glass-card rounded-xl p-6 text-left hover:bg-camel/5 transition-all duration-300 group"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-camel/10 flex items-center justify-center group-hover:bg-camel/20 transition-colors">
                    <Icon className="w-5 h-5 text-camel" />
                  </div>
                  <div>
                    <p className="font-heading font-semibold text-foreground">{action.label}</p>
                    <p className="text-sm text-muted-foreground mt-1">{action.desc}</p>
                  </div>
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
