import { motion } from "framer-motion";
import { Mic, Upload, Users, FileText, Zap, ArrowRight } from "lucide-react";
import heroMesh from "@/assets/hero-mesh.jpg";

interface BentoDashboardProps {
  onModuleChange: (module: string) => void;
}

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24, scale: 0.97 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

const BentoDashboard = ({ onModuleChange }: BentoDashboardProps) => {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="grid grid-cols-12 auto-rows-[140px] gap-4 pb-24"
    >
      {/* Hero — spans full width, 2 rows */}
      <motion.div
        variants={itemVariants}
        className="col-span-12 row-span-2 relative rounded-3xl overflow-hidden bento-glass noise-overlay"
      >
        <img
          src={heroMesh}
          alt=""
          className="absolute inset-0 w-full h-full object-cover opacity-40"
          width={1920}
          height={1080}
        />
        <div className="relative z-10 h-full flex flex-col justify-between p-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl gradient-gold-bright flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-sm font-body font-medium text-muted-foreground tracking-wider uppercase">MeetMind AI</span>
          </div>
          <div>
            <h1 className="text-4xl md:text-5xl font-heading font-extrabold text-foreground leading-tight">
              Your meetings,<br />
              <span className="text-gradient-gold">brilliantly summarized.</span>
            </h1>
            <p className="mt-3 text-muted-foreground max-w-lg text-sm">
              Record, transcribe, identify speakers, and generate actionable summaries — all powered by AI.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Live Recording — large card */}
      <motion.button
        variants={itemVariants}
        onClick={() => onModuleChange("recording")}
        className="col-span-12 md:col-span-5 row-span-2 rounded-3xl bento-glass-hover noise-overlay p-6 text-left group relative overflow-hidden"
      >
        <div className="absolute top-6 right-6 w-20 h-20 rounded-2xl bg-destructive/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
          <div className="w-10 h-10 rounded-full bg-destructive/20 flex items-center justify-center animate-pulse-glow">
            <Mic className="w-5 h-5 text-destructive" />
          </div>
        </div>
        <div className="flex flex-col justify-end h-full">
          <p className="text-xs font-medium text-camel-DEFAULT tracking-wider uppercase mb-2">Start Now</p>
          <h3 className="text-2xl font-heading font-bold text-foreground">Live Recording</h3>
          <p className="text-sm text-muted-foreground mt-1">Capture meetings in real-time with AI transcription</p>
          <div className="flex items-center gap-1 mt-3 text-camel-DEFAULT text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            Begin session <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </motion.button>

      {/* Stats strip — vertical on right */}
      <motion.div
        variants={itemVariants}
        className="col-span-12 md:col-span-7 row-span-2 grid grid-cols-2 gap-4"
      >
        {[
          { label: "Live Capture", value: "Ready", sub: "Mic pipeline available", color: "camel" },
          { label: "Upload", value: "MP3 MP4 WAV", sub: "Auto converts to WAV", color: "olive" },
          { label: "Speaker Split", value: "Diarization", sub: "Timeline + turns", color: "hunter" },
          { label: "Exports", value: "MD PDF DOCX", sub: "From summary view", color: "camel" },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            variants={itemVariants}
            className="rounded-2xl bento-glass noise-overlay p-5 flex flex-col justify-between"
          >
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{stat.label}</p>
            <div>
              <p className="text-3xl font-heading font-extrabold text-foreground">{stat.value}</p>
              <p className="text-xs text-camel-DEFAULT mt-1">{stat.sub}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Upload */}
      <motion.button
        variants={itemVariants}
        onClick={() => onModuleChange("upload")}
        className="col-span-12 md:col-span-4 row-span-2 rounded-3xl bento-glass-hover noise-overlay p-6 text-left group relative overflow-hidden"
      >
        <div className="absolute -bottom-4 -right-4 w-32 h-32 rounded-full bg-camel-DEFAULT/5 group-hover:bg-camel-DEFAULT/10 transition-colors duration-500" />
        <div className="relative z-10 flex flex-col justify-between h-full">
          <div className="w-12 h-12 rounded-2xl bg-camel-DEFAULT/10 flex items-center justify-center">
            <Upload className="w-5 h-5 text-camel-DEFAULT" />
          </div>
          <div>
            <h3 className="text-xl font-heading font-bold text-foreground">Upload Files</h3>
            <p className="text-sm text-muted-foreground mt-1">MP3, MP4, WAV</p>
            <div className="flex items-center gap-1 mt-2 text-camel-DEFAULT text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
              Upload <ArrowRight className="w-4 h-4" />
            </div>
          </div>
        </div>
      </motion.button>

      {/* Diarization */}
      <motion.button
        variants={itemVariants}
        onClick={() => onModuleChange("diarization")}
        className="col-span-12 md:col-span-4 row-span-2 rounded-3xl bento-glass-hover noise-overlay p-6 text-left group"
      >
        <div className="flex flex-col justify-between h-full">
          <div className="w-12 h-12 rounded-2xl bg-hunter/20 flex items-center justify-center">
            <Users className="w-5 h-5 text-accent" />
          </div>
          <div>
            <h3 className="text-xl font-heading font-bold text-foreground">Diarization</h3>
            <p className="text-sm text-muted-foreground mt-1">Who said what</p>
            <div className="flex gap-1 mt-3">
              {[1, 2, 3].map((s) => (
                <div key={s} className="w-7 h-7 rounded-full bg-muted flex items-center justify-center text-[10px] font-bold text-muted-foreground border border-border">
                  S{s}
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.button>

      {/* Summary */}
      <motion.button
        variants={itemVariants}
        onClick={() => onModuleChange("summary")}
        className="col-span-12 md:col-span-4 row-span-2 rounded-3xl bento-glass-hover noise-overlay p-6 text-left group"
      >
        <div className="flex flex-col justify-between h-full">
          <div className="w-12 h-12 rounded-2xl bg-olive/20 flex items-center justify-center">
            <FileText className="w-5 h-5 text-olive" />
          </div>
          <div>
            <h3 className="text-xl font-heading font-bold text-foreground">Summaries</h3>
            <p className="text-sm text-muted-foreground mt-1">AI-powered insights</p>
            <div className="flex items-center gap-1 mt-2 text-camel-DEFAULT text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
              View all <ArrowRight className="w-4 h-4" />
            </div>
          </div>
        </div>
      </motion.button>
    </motion.div>
  );
};

export default BentoDashboard;
