import { AnimatePresence, motion } from "framer-motion";
import { useLocation, useNavigate } from "react-router-dom";
import FloatingDock from "@/components/FloatingDock";
import BentoDashboard from "@/components/BentoDashboard";
import LiveRecordingView from "@/components/LiveRecordingView";
import UploadFileView from "@/components/UploadFileView";
import DiarizationView from "@/components/DiarizationView";
import SummaryView from "@/components/SummaryView";

const moduleToRoute: Record<string, string> = {
  dashboard: "/",
  recording: "/recording",
  upload: "/upload",
  diarization: "/diarization",
  summary: "/summary",
};

function resolveModule(pathname: string): string {
  if (pathname === "/recording") return "recording";
  if (pathname === "/upload") return "upload";
  if (pathname === "/diarization") return "diarization";
  if (pathname === "/summary") return "summary";
  return "dashboard";
}

const Index = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const activeModule = resolveModule(location.pathname);

  const setActiveModule = (module: string) => {
    navigate(moduleToRoute[module] || "/");
  };

  const goBack = () => navigate("/");

  return (
    <div className="min-h-screen bg-background mesh-bg">
      <div className="max-w-6xl mx-auto px-4 md:px-8 pt-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeModule}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            {activeModule === "dashboard" && <BentoDashboard onModuleChange={setActiveModule} />}
            {activeModule === "recording" && <LiveRecordingView onBack={goBack} />}
            {activeModule === "upload" && <UploadFileView onBack={goBack} />}
            {activeModule === "diarization" && <DiarizationView onBack={goBack} />}
            {activeModule === "summary" && (
              <div className="flex flex-col items-center">
                <SummaryView onBack={goBack} />
                <FloatingDock
                  activeModule={activeModule}
                  onModuleChange={setActiveModule}
                  isFixed={false}
                  className="mt-1"
                />
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {activeModule !== "summary" && <FloatingDock activeModule={activeModule} onModuleChange={setActiveModule} />}
    </div>
  );
};

export default Index;
