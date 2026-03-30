import { motion } from "framer-motion";
import { FileText, Users, Clock, Calendar, ChevronRight } from "lucide-react";

const meetingSummary = {
  meetingName: "Q3 Business Review & Q4 Planning",
  date: "March 25, 2026",
  duration: "24 min 58 sec",
  numberOfPersons: 3,
  executiveSummary:
    "The team reviewed Q3 performance metrics showing a 15% increase in user engagement and a 20% decrease in support tickets. Three key focus areas were identified for Q4: platform performance optimization, onboarding flow improvements, and third-party integrations. Action items were assigned with deadlines set for mid-April.",
  clearSummary: [
    {
      topic: "Q3 Performance Review",
      points: [
        "User engagement increased by 15% compared to Q2",
        "Support tickets decreased by 20% following UX improvements",
        "New features launched in July contributed to higher retention rates",
        "Customer satisfaction scores improved to 4.6/5.0",
      ],
    },
    {
      topic: "Q4 Roadmap Priorities",
      points: [
        "Performance optimization — reduce load times by 30%",
        "Redesign onboarding flow for new users",
        "Build integrations with Slack, Jira, and Notion",
        "Launch premium tier with advanced analytics",
      ],
    },
    {
      topic: "Action Items",
      points: [
        "Speaker 1: Compile customer feedback report by April 5",
        "Speaker 2: Draft Q4 marketing plan by April 10",
        "Speaker 3: Prepare technical roadmap and resource allocation by April 15",
      ],
    },
  ],
};

const Summary = () => {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-heading font-bold text-foreground">Meeting Summary</h2>
        <p className="text-muted-foreground mt-1">AI-generated summary of your recorded meetings.</p>
      </div>

      {/* Meeting Meta */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card rounded-2xl p-6"
      >
        <h3 className="text-xl font-heading font-bold text-foreground">{meetingSummary.meetingName}</h3>
        <div className="flex flex-wrap gap-4 mt-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4 text-camel" />
            {meetingSummary.date}
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4 text-camel" />
            {meetingSummary.duration}
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="w-4 h-4 text-camel" />
            {meetingSummary.numberOfPersons} Participants
          </div>
        </div>
      </motion.div>

      {/* Executive Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card rounded-2xl p-6"
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg gradient-camel flex items-center justify-center">
            <FileText className="w-4 h-4 text-primary-foreground" />
          </div>
          <h3 className="text-lg font-heading font-semibold text-foreground">Executive Summary</h3>
        </div>
        <p className="text-foreground/80 leading-relaxed">{meetingSummary.executiveSummary}</p>
      </motion.div>

      {/* Clear Summary */}
      <div className="space-y-4">
        <h3 className="text-lg font-heading font-semibold text-foreground">Detailed Summary</h3>
        {meetingSummary.clearSummary.map((section, i) => (
          <motion.div
            key={section.topic}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="glass-card rounded-xl p-5"
          >
            <h4 className="font-heading font-semibold text-camel mb-3">{section.topic}</h4>
            <ul className="space-y-2">
              {section.points.map((point, j) => (
                <li key={j} className="flex items-start gap-2 text-sm text-foreground/80">
                  <ChevronRight className="w-4 h-4 text-olive mt-0.5 flex-shrink-0" />
                  {point}
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Summary;
