import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Upload, FileAudio, FileVideo, X, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UploadedFile {
  name: string;
  size: string;
  type: string;
  status: "uploading" | "done" | "error";
  progress: number;
}

const UploadFile = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const addFiles = (newFiles: File[]) => {
    const mapped: UploadedFile[] = newFiles
      .filter((f) => /\.(mp3|mp4|wav)$/i.test(f.name))
      .map((f) => ({
        name: f.name,
        size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
        type: f.name.split(".").pop()?.toUpperCase() || "",
        status: "done" as const,
        progress: 100,
      }));
    setFiles((prev) => [...prev, ...mapped]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const getFileIcon = (type: string) => {
    if (type === "MP4") return FileVideo;
    return FileAudio;
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-heading font-bold text-foreground">Upload File</h2>
        <p className="text-muted-foreground mt-1">Upload MP3, MP4, or WAV files for transcription and analysis.</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`glass-card rounded-2xl p-12 border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center cursor-pointer ${
          isDragging ? "border-camel bg-camel/5" : "border-border hover:border-camel/50"
        }`}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.accept = ".mp3,.mp4,.wav";
          input.multiple = true;
          input.onchange = (e) => {
            const target = e.target as HTMLInputElement;
            if (target.files) addFiles(Array.from(target.files));
          };
          input.click();
        }}
      >
        <div className="w-16 h-16 rounded-full bg-camel/10 flex items-center justify-center mb-4">
          <Upload className="w-7 h-7 text-camel" />
        </div>
        <p className="font-heading font-semibold text-foreground text-lg">Drop files here or click to browse</p>
        <p className="text-sm text-muted-foreground mt-2">Supports MP3, MP4, and WAV formats</p>
      </motion.div>

      {files.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-heading font-semibold text-foreground">Uploaded Files</h3>
          {files.map((file, i) => {
            const Icon = getFileIcon(file.type);
            return (
              <motion.div
                key={`${file.name}-${i}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass-card rounded-xl p-4 flex items-center gap-4"
              >
                <div className="w-10 h-10 rounded-lg bg-camel/10 flex items-center justify-center">
                  <Icon className="w-5 h-5 text-camel" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{file.size} · {file.type}</p>
                </div>
                <CheckCircle className="w-5 h-5 text-olive" />
                <button onClick={() => removeFile(i)} className="text-muted-foreground hover:text-destructive transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}
          <Button className="mt-4 gradient-camel text-primary-foreground hover:opacity-90">
            Process Files
          </Button>
        </div>
      )}
    </div>
  );
};

export default UploadFile;
