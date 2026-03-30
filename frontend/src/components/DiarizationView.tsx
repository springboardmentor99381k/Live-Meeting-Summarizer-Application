import { motion } from "framer-motion";
import { useMemo } from "react";
import { Users, User, ArrowLeft } from "lucide-react";
import { getLastPipeline } from "@/lib/meeting-session";

interface DiarizationViewProps {
  onBack: () => void;
}

const speakerColors = ["hsl(37,40%,52%)", "hsl(130,22%,40%)", "hsl(63,43%,45%)"];

function toDuration(seconds: number): string {
  const rounded = Math.max(0, Math.round(seconds));
  const m = Math.floor(rounded / 60);
  const s = rounded % 60;
  return `${m}m ${s.toString().padStart(2, "0")}s`;
}

function timelineFromConversation(text: string) {
  const lines = (text || "").split("\n");
  const entries: Array<{ s: number; t: string; text: string }> = [];

  for (const line of lines) {
    const match = line.match(/^(SPEAKER[_\s-]?(\d+))\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*(\d{1,2}:\d{2}(?::\d{2})?)\]\s*:\s*(.+)$/i);
    if (!match) {
      continue;
    }

    entries.push({
      s: Number(match[2]) + 1,
      t: `${match[3]} - ${match[4]}`,
      text: match[5],
    });
  }

  return entries;
}

const DiarizationView = ({ onBack }: DiarizationViewProps) => {
  const pipeline = getLastPipeline();

  const { speakers, timeline } = useMemo(() => {
    if (!pipeline) {
      return { speakers: [], timeline: [] };
    }

    const speakerTotals = new Map<string, { segments: number; totalSeconds: number }>();
    let allSeconds = 0;

    for (const segment of pipeline.segments || []) {
      const start = Number(segment.start || 0);
      const end = Number(segment.end || start);
      const duration = Math.max(0, end - start);
      const key = String(segment.speaker || "SPEAKER_00");

      const existing = speakerTotals.get(key) || { segments: 0, totalSeconds: 0 };
      existing.segments += 1;
      existing.totalSeconds += duration;
      speakerTotals.set(key, existing);
      allSeconds += duration;
    }

    const sorted = [...speakerTotals.entries()].sort((a, b) => b[1].totalSeconds - a[1].totalSeconds);
    const speakerList = sorted.map(([name, values], index) => ({
      id: index + 1,
      name,
      segments: values.segments,
      duration: toDuration(values.totalSeconds),
      pct: allSeconds > 0 ? Math.round((values.totalSeconds / allSeconds) * 100) : 0,
    }));

    const timelineList = timelineFromConversation(pipeline.conversation_text || "");
    return { speakers: speakerList, timeline: timelineList };
  }, [pipeline]);

  return (
    <div className="pb-24">
      <button onClick={onBack} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Hub
      </button>

      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
        <div>
          <h2 className="text-3xl font-heading font-extrabold text-foreground">Speaker Diarization</h2>
          <p className="text-muted-foreground text-sm mt-1">Identify who said what in your meeting.</p>
        </div>

        {!pipeline && (
          <div className="rounded-2xl border border-border/60 bg-background/40 p-5 text-sm text-muted-foreground">
            No processed meeting found yet. Upload a file or stop a live recording to generate diarization output.
          </div>
        )}

        {/* Speaker overview bar */}
        <div className="rounded-3xl bento-glass noise-overlay p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-4 h-4 text-camel-DEFAULT" />
            <span className="text-sm font-medium text-muted-foreground">Conversation Distribution</span>
          </div>
          <div className="flex h-4 rounded-full overflow-hidden gap-1">
            {speakers.map((sp, i) => (
              <motion.div
                key={sp.id}
                initial={{ width: 0 }}
                animate={{ width: `${sp.pct}%` }}
                transition={{ duration: 1, delay: 0.3 + i * 0.15, ease: [0.22, 1, 0.36, 1] }}
                className="h-full rounded-full"
                style={{ backgroundColor: speakerColors[i % speakerColors.length] }}
              />
            ))}
          </div>
          <div className="flex gap-6 mt-4">
            {speakers.map((sp, i) => (
              <div key={sp.id} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: speakerColors[i % speakerColors.length] }} />
                <span className="text-xs text-muted-foreground">{sp.name} · {sp.pct}%</span>
              </div>
            ))}
            {speakers.length === 0 && <span className="text-xs text-muted-foreground">No speaker segments available.</span>}
          </div>
        </div>

        {/* Speaker cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {speakers.map((sp, i) => (
            <motion.div
              key={sp.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
              className="rounded-2xl bento-glass noise-overlay p-5"
            >
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-11 h-11 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${speakerColors[i % speakerColors.length]}15`, border: `2px solid ${speakerColors[i % speakerColors.length]}` }}
                >
                  <User className="w-4 h-4" style={{ color: speakerColors[i % speakerColors.length] }} />
                </div>
                <div>
                  <p className="font-heading font-bold text-foreground text-sm">{sp.name}</p>
                  <p className="text-xs text-muted-foreground">{sp.segments} segments</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">Duration: <span className="text-foreground font-medium">{sp.duration}</span></p>
            </motion.div>
          ))}
        </div>

        {/* Timeline */}
        <div className="space-y-2">
          <h3 className="text-lg font-heading font-bold text-foreground mb-3">Timeline</h3>
          {timeline.map((entry, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + i * 0.06 }}
              className="rounded-2xl bento-glass p-4 flex gap-4 group hover:border-border/80 transition-colors"
            >
              <div
                className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                style={{
                  backgroundColor: `${speakerColors[(entry.s - 1) % speakerColors.length]}15`,
                  color: speakerColors[(entry.s - 1) % speakerColors.length],
                  border: `2px solid ${speakerColors[(entry.s - 1) % speakerColors.length]}`,
                }}
              >
                S{entry.s}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold" style={{ color: speakerColors[(entry.s - 1) % speakerColors.length] }}>Speaker {entry.s}</span>
                  <span className="text-xs text-muted-foreground">{entry.t}</span>
                </div>
                <p className="text-sm text-foreground/75 leading-relaxed">{entry.text}</p>
              </div>
            </motion.div>
          ))}
          {timeline.length === 0 && (
            <div className="rounded-2xl border border-border/60 bg-background/40 p-4 text-sm text-muted-foreground">
              Timeline entries will appear after a pipeline run generates conversation text.
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default DiarizationView;
