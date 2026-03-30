import { motion } from "framer-motion";
import { Users, User } from "lucide-react";

const speakers = [
  { id: 1, name: "Speaker 1", color: "hsl(37, 40%, 52%)", segments: 12, duration: "8m 42s", percentage: 35 },
  { id: 2, name: "Speaker 2", color: "hsl(130, 22%, 40%)", segments: 9, duration: "6m 15s", percentage: 25 },
  { id: 3, name: "Speaker 3", color: "hsl(63, 43%, 45%)", segments: 15, duration: "10m 03s", percentage: 40 },
];

const timeline = [
  { speaker: 1, start: "00:00", end: "02:15", text: "Let's kick off the meeting. Today we'll be discussing Q3 results and the roadmap for Q4..." },
  { speaker: 2, start: "02:15", end: "05:30", text: "Thanks. Looking at the numbers, we've seen a 15% increase in user engagement..." },
  { speaker: 3, start: "05:30", end: "08:12", text: "That aligns with what we saw on the product side. The new features launched in July..." },
  { speaker: 1, start: "08:12", end: "10:45", text: "Great insights. Let me now share the customer feedback we've been collecting..." },
  { speaker: 2, start: "10:45", end: "14:00", text: "I'd also like to add that the support tickets have decreased by 20%..." },
  { speaker: 3, start: "14:00", end: "18:30", text: "For Q4, I propose we focus on three key areas: performance, onboarding, and integrations..." },
];

const Diarization = () => {
  const getSpeakerColor = (id: number) => speakers.find((s) => s.id === id)?.color || "";

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-heading font-bold text-foreground">Speaker Diarization</h2>
        <p className="text-muted-foreground mt-1">Identify and separate speakers from your meeting recordings.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {speakers.map((speaker, i) => (
          <motion.div
            key={speaker.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card rounded-xl p-5"
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${speaker.color}20`, border: `2px solid ${speaker.color}` }}
              >
                <User className="w-4 h-4" style={{ color: speaker.color }} />
              </div>
              <div>
                <p className="font-heading font-semibold text-foreground">{speaker.name}</p>
                <p className="text-xs text-muted-foreground">{speaker.segments} segments · {speaker.duration}</p>
              </div>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${speaker.percentage}%` }}
                transition={{ duration: 1, delay: 0.5 + i * 0.2 }}
                className="h-full rounded-full"
                style={{ backgroundColor: speaker.color }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-1">{speaker.percentage}% of conversation</p>
          </motion.div>
        ))}
      </div>

      <div>
        <h3 className="text-lg font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-camel" /> Conversation Timeline
        </h3>
        <div className="space-y-3">
          {timeline.map((entry, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="glass-card rounded-xl p-4 flex gap-4"
            >
              <div className="flex flex-col items-center">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{
                    backgroundColor: `${getSpeakerColor(entry.speaker)}20`,
                    color: getSpeakerColor(entry.speaker),
                    border: `2px solid ${getSpeakerColor(entry.speaker)}`,
                  }}
                >
                  S{entry.speaker}
                </div>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium" style={{ color: getSpeakerColor(entry.speaker) }}>
                    Speaker {entry.speaker}
                  </span>
                  <span className="text-xs text-muted-foreground">{entry.start} - {entry.end}</span>
                </div>
                <p className="text-sm text-foreground/80">{entry.text}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Diarization;
