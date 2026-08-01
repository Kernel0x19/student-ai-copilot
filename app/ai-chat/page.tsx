"use client";

import { useEffect, useRef, useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { createClient } from "@/app/lib/supabase/client";

interface Message {
  role: string;
  text: string;
  sources?: Array<{
    title: string;
    category: string;
    ministry: string;
    state: string;
    official_link: string;
  }>;
}

type SpeechRecognitionResultEvent = Event & {
  resultIndex: number;
  results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>;
};

type SpeechRecognition = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionResultEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
};

type SpeechRecognitionConstructor = new () => SpeechRecognition;

export default function AIChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [user, setUser] = useState<{ id: string; email?: string } | null>(null);
  const [voiceLanguage, setVoiceLanguage] = useState("en-IN");
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const shouldListenRef = useRef(false);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => setUser(data.user ? { id: data.user.id, email: data.user.email } : null));
  }, []);

  useEffect(() => () => {
    shouldListenRef.current = false;
    recognitionRef.current?.stop();
  }, []);

  const toggleVoiceInput = () => {
    if (shouldListenRef.current) {
      shouldListenRef.current = false;
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    const voiceWindow = window as typeof window & {
      SpeechRecognition?: SpeechRecognitionConstructor;
      webkitSpeechRecognition?: SpeechRecognitionConstructor;
    };
    const SpeechRecognition = voiceWindow.SpeechRecognition || voiceWindow.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError("Voice input works in Chrome or Edge. Please open this page in one of those browsers.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = voiceLanguage;
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result[0].transcript.trim();
        if (result.isFinal && transcript) {
          setInput((current) => `${current}${current ? " " : ""}${transcript}`);
        }
      }
    };
    recognition.onend = () => {
      if (!shouldListenRef.current) {
        setIsListening(false);
        return;
      }
      window.setTimeout(() => {
        if (!shouldListenRef.current) return;
        try { recognition.start(); } catch { setIsListening(false); shouldListenRef.current = false; }
      }, 150);
    };
    recognition.onerror = () => {
      shouldListenRef.current = false;
      setIsListening(false);
      setVoiceError("Microphone access was blocked or speech was not recognised. Allow microphone permission and try again.");
    };
    recognitionRef.current = recognition;
    shouldListenRef.current = true;
    setVoiceError("");
    setIsListening(true);
    try { recognition.start(); } catch {
      shouldListenRef.current = false;
      setIsListening(false);
      setVoiceError("Voice recognition could not start. Please try again.");
    }
  };

  const sendMessage = async () => {
    if (!input.trim() && !file) return;
    const userMsg = input.trim() || `Uploaded ${file?.name}`;
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const headers = { "X-User-Id": user?.id || "", "X-User-Email": user?.email || "" };
      const res = file
        ? await (() => { const form = new FormData(); form.append("file", file); form.append("message", input.trim()); form.append("attach_to_profile", "true"); return fetch(`${apiBase}/api/v1/chat/upload`, { method: "POST", headers, body: form }); })()
        : await fetch(`${apiBase}/api/v1/chat/`, { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body: JSON.stringify({ message: userMsg }) });
      const data = await res.json();
      if (data.response) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: data.response, sources: data.sources },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", text: "Error: no response" },
        ]);
      }
    } catch (e) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error contacting server" },
      ]);
    } finally {
      setFile(null);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen p-4 bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">AI Chat - Student Schemes Assistant</h1>
      <div className="flex-1 overflow-y-auto mb-4 p-4 bg-white rounded shadow space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg mb-2">Ask me about student schemes!</p>
            <p className="text-sm">Try asking:</p>
            <ul className="text-sm mt-2 space-y-1">
              <li>&quot;What scholarships are available for engineering students?&quot;</li>
              <li>&quot;Tell me about schemes in Karnataka&quot;</li>
              <li>&quot;What are the eligibility criteria for AICTE schemes?&quot;</li>
            </ul>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                msg.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-900"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.text}</p>
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="max-w-[80%] mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm font-semibold text-blue-900 mb-2">📚 Sources:</p>
                {msg.sources.map((source, srcIdx) => (
                  <div key={srcIdx} className="text-xs text-blue-800 mb-2 pb-2 border-b border-blue-200 last:border-0">
                    <p className="font-semibold">{source.title}</p>
                    <p className="text-blue-600">
                      {source.category} • {source.state}
                    </p>
                    {source.official_link && (
                      <a
                        href={source.official_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 underline hover:text-blue-700"
                      >
                        Official Link →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center text-gray-500">
            <div className="animate-pulse">Searching schemes and generating response...</div>
          </div>
        )}
      </div>
      {voiceError && <p className="mb-2 text-sm text-red-600">{voiceError}</p>}
      <div className="flex gap-2">
        <select value={voiceLanguage} onChange={(event) => setVoiceLanguage(event.target.value)} disabled={loading || isListening} className="border rounded-lg px-2 text-sm" aria-label="Voice language">
          <option value="en-IN">English</option>
          <option value="hi-IN">हिन्दी</option>
          <option value="mr-IN">मराठी</option>
        </select>
        <button type="button" onClick={toggleVoiceInput} disabled={loading} className={`px-3 py-2 border rounded-lg ${isListening ? "bg-red-600 text-white" : "bg-white"}`} aria-label={isListening ? "Stop listening" : "Start voice input"} title={isListening ? "Listening — tap to stop" : "Tap to speak"}>
          {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </button>
        <input ref={fileInput} type="file" className="hidden" accept="image/*,.pdf" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        <button type="button" onClick={() => fileInput.current?.click()} disabled={loading} className="px-3 py-2 border rounded-lg" aria-label="Attach document">📎</button>
        <input
          type="text"
          className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && sendMessage()}
          placeholder={file ? `Attached: ${file.name}` : "Ask about student schemes, scholarships, eligibility..."}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || (!input.trim() && !file)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50 hover:bg-blue-700 transition-colors font-medium"
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
