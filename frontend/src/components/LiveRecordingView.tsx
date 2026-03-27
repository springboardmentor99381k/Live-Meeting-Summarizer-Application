import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Mic, MicOff, Pause, Square, Clock, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { getLiveTranscript, runPipeline, startRecording, stopRecording } from "@/lib/api";
import { saveLastPipeline } from "@/lib/meeting-session";

interface LiveRecordingViewProps {
  onBack: () => void;
}

const LiveRecordingView = ({ onBack }: LiveRecordingViewProps) => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [statusText, setStatusText] = useState("");
  const [errorText, setErrorText] = useState("");
  const [liveTranscript, setLiveTranscript] = useState("");

  useEffect(() => {
    if (!isRecording || isPaused) {
      return;
    }

    const timer = window.setInterval(() => {
      setElapsedSeconds((value) => value + 1);
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isPaused, isRecording]);

  useEffect(() => {
    if (!isRecording || isPaused) {
      return;
    }

    const poller = window.setInterval(async () => {
      try {
        const result = await getLiveTranscript();
        setLiveTranscript(result.transcript || "");
      } catch {
        // Keep recording UI responsive even if polling fails.
      }
    }, 1500);

    return () => window.clearInterval(poller);
  }, [isPaused, isRecording]);

  const formatClock = (seconds: number): string => {
    const h = Math.floor(seconds / 3600)
      .toString()
      .padStart(2, "0");
    const m = Math.floor((seconds % 3600) / 60)
      .toString()
      .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${h}:${m}:${s}`;
  };

  const handleRecordToggle = async () => {
    setErrorText("");

    if (!isRecording) {
      try {
        setStatusText("Starting recording...");
        await startRecording();
        setLiveTranscript("");
        setElapsedSeconds(0);
        setIsPaused(false);
        setIsRecording(true);
        setStatusText("Recording in progress.");
      } catch (error) {
        setStatusText("");
        setErrorText(error instanceof Error ? error.message : "Could not start recording.");
      }
      return;
    }

    await handleStopAndProcess();
  };

  const handleStopAndProcess = async () => {
    if (!isRecording) {
      return;
    }

    setErrorText("");

    try {
      setStatusText("Stopping recording...");
      const stopResult = await stopRecording();
      setIsRecording(false);
      setIsPaused(false);

      setStatusText("Running transcript, diarization, and summary pipeline...");
      const pipelineResult = await runPipeline({ wavPath: stopResult.wav_path });
      saveLastPipeline(pipelineResult);

      setStatusText("Done. Opening summary.");
      navigate("/summary");
    } catch (error) {
      setStatusText("");
      setErrorText(error instanceof Error ? error.message : "Could not stop recording.");
    }
  };

  return (
    <div className="pb-24">
      <button onClick={onBack} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Hub
      </button>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl bento-glass noise-overlay p-8 md:p-12 flex flex-col items-center"
      >
        <h2 className="text-3xl font-heading font-extrabold text-foreground mb-2">Live Recording</h2>
        <p className="text-muted-foreground text-sm mb-10">Capture your meeting in real-time</p>

        <div className="relative">
          {isRecording && !isPaused && (
            <>
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-destructive/30"
                animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-destructive/20"
                animate={{ scale: [1, 1.9], opacity: [0.4, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
              />
            </>
          )}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRecordToggle}
            className={`relative z-10 w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 ${
              isRecording
                ? "bg-destructive/15 border-2 border-destructive glow-active"
                : "bg-camel-DEFAULT/10 border-2 border-camel-DEFAULT/50 hover:border-camel-DEFAULT"
            }`}
          >
            {isRecording ? (
              <MicOff className="w-10 h-10 text-destructive" />
            ) : (
              <Mic className="w-10 h-10 text-camel-DEFAULT" />
            )}
          </motion.button>
        </div>

        <div className="mt-8 flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <span className="text-4xl font-heading font-bold text-foreground tabular-nums tracking-tight">{formatClock(elapsedSeconds)}</span>
        </div>

        <p className="text-muted-foreground mt-2 text-sm">
          {isRecording ? (isPaused ? "Paused" : "Recording...") : "Tap to begin"}
        </p>

        {isRecording && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 mt-8"
          >
            <Button
              variant="outline"
              onClick={() => setIsPaused(!isPaused)}
              className="border-border text-foreground hover:bg-muted rounded-xl"
            >
              <Pause className="w-4 h-4 mr-2" />
              {isPaused ? "Resume" : "Pause"}
            </Button>
            <Button
              variant="destructive"
              onClick={handleStopAndProcess}
              className="rounded-xl"
            >
              <Square className="w-4 h-4 mr-2" />
              Stop & Save
            </Button>
          </motion.div>
        )}

        {statusText && <p className="mt-6 text-xs text-muted-foreground">{statusText}</p>}
        {errorText && <p className="mt-2 text-xs text-destructive">{errorText}</p>}

        {liveTranscript && (
          <div className="mt-6 w-full max-w-2xl rounded-xl border border-border/60 bg-background/40 p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">Live Transcript</p>
            <p className="text-sm text-foreground/80 leading-relaxed whitespace-pre-wrap">{liveTranscript}</p>
          </div>
        )}

        {isRecording && !isPaused && (
          <div className="mt-10 w-full max-w-md flex items-end justify-center gap-[3px] h-12">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                className="w-[3px] rounded-full bg-camel-DEFAULT/50"
                animate={{
                  height: [6, Math.random() * 36 + 6, 6],
                }}
                transition={{
                  duration: 0.4 + Math.random() * 0.6,
                  repeat: Infinity,
                  delay: i * 0.03,
                  ease: "easeInOut",
                }}
              />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default LiveRecordingView;
