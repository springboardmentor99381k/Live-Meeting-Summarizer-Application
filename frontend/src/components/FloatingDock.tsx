import { motion } from "framer-motion";
import { Mic, Upload, Users, FileText, LayoutGrid } from "lucide-react";
import { cn } from "@/lib/utils";

interface FloatingDockProps {
  activeModule: string;
  onModuleChange: (module: string) => void;
  className?: string;
  isFixed?: boolean;
}

const dockItems = [
  { id: "dashboard", label: "Hub", icon: LayoutGrid },
  { id: "recording", label: "Record", icon: Mic },
  { id: "upload", label: "Upload", icon: Upload },
  { id: "diarization", label: "Speakers", icon: Users },
  { id: "summary", label: "Summary", icon: FileText },
];

const FloatingDock = ({ activeModule, onModuleChange, className, isFixed = true }: FloatingDockProps) => {
  return (
    <motion.div
      initial={{ y: 80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, type: "spring", stiffness: 200, damping: 25 }}
      className={cn(isFixed ? "fixed bottom-6 left-1/2 -translate-x-1/2 z-50" : "z-40", className)}
    >
      <div className="dock-blur rounded-2xl px-2 py-2 flex items-center gap-1">
        {dockItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeModule === item.id;
          return (
            <motion.button
              key={item.id}
              onClick={() => onModuleChange(item.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className={cn(
                "relative flex flex-col items-center gap-1 px-4 py-2.5 rounded-xl transition-all duration-300",
                isActive ? "bg-primary/15" : "hover:bg-muted/40"
              )}
            >
              <Icon
                className={cn(
                  "w-5 h-5 transition-colors duration-300",
                  isActive ? "text-camel-DEFAULT" : "text-muted-foreground"
                )}
              />
              <span
                className={cn(
                  "text-[10px] font-medium transition-colors duration-300",
                  isActive ? "text-camel-DEFAULT" : "text-muted-foreground"
                )}
              >
                {item.label}
              </span>
              {isActive && (
                <motion.div
                  layoutId="dock-indicator"
                  className="absolute -bottom-0.5 w-5 h-0.5 rounded-full gradient-gold-bright"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default FloatingDock;
