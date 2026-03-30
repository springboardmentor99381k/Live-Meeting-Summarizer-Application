import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileAudio, FileVideo, X, CheckCircle, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { runPipeline, uploadAudio } from "@/lib/api";
import { saveLastPipeline } from "@/lib/meeting-session";

interface UploadedFile {
  name: string;
  size: string;
  type: string;
  raw: File;
}

interface UploadFileViewProps {
  onBack: () => void;
}

const UploadFileView = ({ onBack }: UploadFileViewProps) => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [errorText, setErrorText] = useState("");

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    addFiles(Array.from(e.dataTransfer.files));
  }, []);

  const addFiles = (newFiles: File[]) => {
    const mapped: UploadedFile[] = newFiles
      .filter((f) => /\.(mp3|mp4|wav)$/i.test(f.name))
      .map((f) => ({
        name: f.name,
        size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
        type: f.name.split(".").pop()?.toUpperCase() || "",
        raw: f,
      }));
    setFiles((prev) => [...prev, ...mapped]);
  };

  const processFiles = async () => {
    if (files.length === 0 || isProcessing) {
      return;
    }

    setIsProcessing(true);
    setErrorText("");

    try {
      const first = files[0];
      setStatusText(`Uploading ${first.name}...`);
      const uploadResult = await uploadAudio(first.raw);

      setStatusText("Running transcript, diarization, and summary pipeline...");
      const pipelineResult = await runPipeline({ wavPath: uploadResult.wav_path });
      saveLastPipeline(pipelineResult);

      setStatusText("Done. Opening summary.");
      navigate("/summary");
    } catch (error) {
      setErrorText(error instanceof Error ? error.message : "Upload failed.");
      setStatusText("");
    } finally {
      setIsProcessing(false);
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
        className="space-y-6"
      >
        <div>
          <h2 className="text-3xl font-heading font-extrabold text-foreground">Upload Files</h2>
          <p className="text-muted-foreground text-sm mt-1">Drag & drop MP3, MP4, or WAV files</p>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => {
            const input = document.createElement("input");
            input.type = "file";
            input.accept = ".mp3,.mp4,.wav";
            input.multiple = true;
            input.onchange = (e) => {
              const t = e.target as HTMLInputElement;
              if (t.files) addFiles(Array.from(t.files));
            };
            input.click();
          }}
          className={`rounded-3xl bento-glass noise-overlay p-16 border-2 border-dashed transition-all duration-500 flex flex-col items-center cursor-pointer ${
            isDragging ? "border-camel-DEFAULT bg-camel-DEFAULT/5 glow-soft" : "border-border hover:border-camel-DEFAULT/40"
          }`}
        >
          <motion.div
            animate={isDragging ? { scale: 1.1, y: -4 } : { scale: 1, y: 0 }}
            className="w-20 h-20 rounded-2xl bg-camel-DEFAULT/10 flex items-center justify-center mb-5"
          >
            <Upload className="w-8 h-8 text-camel-DEFAULT" />
          </motion.div>
          <p className="font-heading font-bold text-foreground text-lg">Drop files here</p>
          <p className="text-sm text-muted-foreground mt-1">or click to browse your device</p>
          <div className="flex gap-2 mt-4">
            {["MP3", "MP4", "WAV"].map((fmt) => (
              <span key={fmt} className="px-3 py-1 rounded-full bg-muted text-xs font-medium text-muted-foreground">{fmt}</span>
            ))}
          </div>
        </div>

        <AnimatePresence>
          {files.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
              {files.map((file, i) => {
                const Icon = file.type === "MP4" ? FileVideo : FileAudio;
                return (
                  <motion.div
                    key={`${file.name}-${i}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="rounded-2xl bento-glass p-4 flex items-center gap-4"
                  >
                    <div className="w-10 h-10 rounded-xl bg-camel-DEFAULT/10 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-camel-DEFAULT" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                      <p className="text-xs text-muted-foreground">{file.size} · {file.type}</p>
                    </div>
                    <CheckCircle className="w-5 h-5 text-olive flex-shrink-0" />
                    <button onClick={() => setFiles((p) => p.filter((_, j) => j !== i))} className="text-muted-foreground hover:text-destructive transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  </motion.div>
                );
              })}
              <Button
                onClick={processFiles}
                disabled={isProcessing}
                className="gradient-gold-bright text-primary-foreground hover:opacity-90 rounded-xl mt-2"
              >
                {isProcessing ? "Processing..." : `Process ${files.length} file${files.length > 1 ? "s" : ""}`}
              </Button>
              {statusText && <p className="text-xs text-muted-foreground">{statusText}</p>}
              {errorText && <p className="text-xs text-destructive">{errorText}</p>}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default UploadFileView;
