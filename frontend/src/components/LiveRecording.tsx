import { useState } from "react";
import { motion } from "framer-motion";
import { Mic, MicOff, Pause, Square, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";

const LiveRecording = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsed, setElapsed] = useState("00:00:00");

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-heading font-bold text-foreground">Live Recording</h2>
        <p className="text-muted-foreground mt-1">Record your meetings in real-time for AI-powered analysis.</p>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card rounded-2xl p-10 flex flex-col items-center justify-center"
      >
        <div className="relative">
          {isRecording && !isPaused && (
            <>
              <div className="absolute inset-0 rounded-full bg-destructive/20 animate-pulse-ring" />
              <div className="absolute inset-0 rounded-full bg-destructive/10 animate-pulse-ring" style={{ animationDelay: "0.5s" }} />
            </>
          )}
          <button
            onClick={() => setIsRecording(!isRecording)}
            className={`relative z-10 w-28 h-28 rounded-full flex items-center justify-center transition-all duration-300 ${
              isRecording
                ? "bg-destructive/20 border-2 border-destructive"
                : "bg-camel/15 border-2 border-camel hover:bg-camel/25"
            }`}
          >
            {isRecording ? (
              <MicOff className="w-10 h-10 text-destructive" />
            ) : (
              <Mic className="w-10 h-10 text-camel" />
            )}
          </button>
        </div>

        <div className="mt-8 flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <span className="text-3xl font-heading font-bold text-foreground tabular-nums">{elapsed}</span>
        </div>

        <p className="text-muted-foreground mt-2 text-sm">
          {isRecording ? (isPaused ? "Paused" : "Recording in progress...") : "Click to start recording"}
        </p>

        {isRecording && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 mt-6"
          >
            <Button
              variant="outline"
              onClick={() => setIsPaused(!isPaused)}
              className="border-border text-foreground hover:bg-muted"
            >
              <Pause className="w-4 h-4 mr-2" />
              {isPaused ? "Resume" : "Pause"}
            </Button>
            <Button
              variant="destructive"
              onClick={() => { setIsRecording(false); setIsPaused(false); }}
            >
              <Square className="w-4 h-4 mr-2" />
              Stop
            </Button>
          </motion.div>
        )}

        {/* Waveform visualization placeholder */}
        {isRecording && !isPaused && (
          <div className="mt-8 w-full flex items-center justify-center gap-1">
            {Array.from({ length: 40 }).map((_, i) => (
              <motion.div
                key={i}
                className="w-1 rounded-full bg-camel/60"
                animate={{ height: [8, Math.random() * 32 + 8, 8] }}
                transition={{ duration: 0.5 + Math.random() * 0.5, repeat: Infinity, delay: i * 0.05 }}
              />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default LiveRecording;
