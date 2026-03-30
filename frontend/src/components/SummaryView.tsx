import { motion } from "framer-motion";
import { FileText, Users, Clock, Calendar, ChevronRight, ArrowLeft, Sparkles } from "lucide-react";
import { getLastPipeline } from "@/lib/meeting-session";

interface SummaryViewProps {
  onBack: () => void;
}

function parseSummaryText(summary: string) {
  const text = (summary || "").trim();

  const titleMatch = text.match(/Title:\s*(.+)/i);
  const durationMatch = text.match(/Duration:\s*(.+)/i);
  const speakersMatch = text.match(/No of Speakers:\s*(\d+)/i);
  const execMatch = text.match(/Executive Summary:\s*([\s\S]*?)\n\s*Key Discussion Points:/i);
  const keyMatch = text.match(/Key Discussion Points:\s*([\s\S]*)$/i);

  const keyPoints = (keyMatch?.[1] || "")
    .split("\n")
    .map((line) => line.replace(/^[-*\d.)\s]+/, "").trim())
    .filter(Boolean);

  return {
    title: titleMatch?.[1]?.trim() || "Meeting Notes",
    duration: durationMatch?.[1]?.trim() || "0:00",
    speakers: Number(speakersMatch?.[1] || 0),
    executive: execMatch?.[1]?.trim() || "No executive summary generated yet.",
    keyPoints,
  };
}

const SummaryView = ({ onBack }: SummaryViewProps) => {
  const pipeline = getLastPipeline();
  const parsed = parseSummaryText(pipeline?.summary || "");

  const meetingName = pipeline?.meeting_title || parsed.title;
  const duration = pipeline?.duration || parsed.duration;
  const participants = pipeline?.speaker_count || parsed.speakers;
  const meetingDate = new Date().toLocaleDateString();

  const sections = [
    {
      topic: "Key Discussion Points",
      points: parsed.keyPoints.length > 0 ? parsed.keyPoints : ["No key discussion points available yet."],
    },
  ];

  return (
    <div className="pb-24">
      <button onClick={onBack} className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6 text-sm">
        <ArrowLeft className="w-4 h-4" /> Back to Hub
      </button>

      <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
        {/* Meeting header */}
        <div className="rounded-3xl bento-glass noise-overlay p-8">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-camel-DEFAULT" />
            <span className="text-xs font-medium text-camel-DEFAULT tracking-wider uppercase">AI Generated Summary</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-heading font-extrabold text-foreground">{meetingName}</h2>
          <div className="flex flex-wrap gap-5 mt-5">
            {[
              { icon: Calendar, text: meetingDate },
              { icon: Clock, text: duration },
              { icon: Users, text: `${participants} Participants` },
            ].map((meta, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                <meta.icon className="w-4 h-4 text-camel-DEFAULT" />
                {meta.text}
              </div>
            ))}
          </div>
        </div>

        {!pipeline && (
          <div className="rounded-2xl border border-border/60 bg-background/40 p-5 text-sm text-muted-foreground">
            No summary generated yet. Process an upload or stop a live recording to view AI output here.
          </div>
        )}

        {/* Executive summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="rounded-3xl bento-glass noise-overlay p-8"
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl gradient-gold-bright flex items-center justify-center">
              <FileText className="w-5 h-5 text-primary-foreground" />
            </div>
            <h3 className="text-lg font-heading font-bold text-foreground">Executive Summary</h3>
          </div>
          <p className="text-foreground/80 leading-relaxed text-[15px]">{parsed.executive}</p>
        </motion.div>

        {/* Detailed sections */}
        <div className="w-full flex flex-col items-center">
          {sections.map((section, i) => (
            <motion.div
              key={section.topic}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="w-full max-w-5xl rounded-2xl bento-glass noise-overlay p-6 flex flex-col mb-10"
            >
              <h4 className="font-heading font-bold text-camel-DEFAULT text-sm mb-4 tracking-wide">{section.topic}</h4>
              <ul className="space-y-3 flex-1">
                {section.points.map((point, j) => (
                  <li key={j} className="flex items-start gap-4 text-sm text-foreground/75 leading-relaxed">
                    <ChevronRight className="w-3.5 h-3.5 text-olive mt-1 flex-shrink-0" />
                    <span className="flex-1">{point}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default SummaryView;
