"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { Session } from "@supabase/supabase-js";
import {
  Send,
  MessageSquare,
  Bot,
  User,
  Loader2,
  Sparkles,
  Trash2,
  Copy,
  Check,
  Paperclip,
  X,
  Mic,
  MicOff,
  ChevronDown,
} from "lucide-react";
import { createClient } from "@/app/lib/supabase/client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Source[];
}

interface Source {
  title: string;
  category: string;
  relevance_score: number;
  deadline: string | null;
  amount: number | null;
}

interface ChatThread {
  id: string;
  title: string;
  updated_at: string;
}

type SpeechRecognitionEvent = Event & {
  resultIndex: number;
  results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>;
};

type SpeechRecognitionErrorEvent = Event & { error: string };

type SpeechRecognitionInstance = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onend: (() => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionInstance;

export default function ChatPage() {
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>("");
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [voiceLanguage, setVoiceLanguage] = useState("en-IN");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const shouldListenRef = useRef(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const authHeaders = useCallback(
    () => ({
      "X-User-Id": session?.user.id || "",
      "X-User-Email": session?.user.email || "",
    }),
    [session]
  );

  const loadThreads = useCallback(async () => {
    if (!session?.user) return;
    const response = await fetch(`${API_BASE}/api/v1/chat/threads`, {
      headers: authHeaders(),
    });
    if (response.ok) {
      const data = await response.json();
      setThreads(data.threads || []);
    }
  }, [API_BASE, authHeaders, session]);

  const loadThread = async (selectedThreadId: string) => {
    if (!selectedThreadId) return;
    const response = await fetch(
      `${API_BASE}/api/v1/chat/history/${selectedThreadId}`,
      { headers: authHeaders() }
    );
    if (!response.ok) return;
    const data = await response.json();
    setThreadId(selectedThreadId);
    setMessages(
      data.history.map(
        (
          message: { role: "user" | "assistant"; content: string },
          index: number
        ) => ({
          id: `${selectedThreadId}-${index}`,
          role: message.role,
          content: message.content,
          timestamp: new Date(),
        })
      )
    );
    setError(null);
  };

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      loadThreads().catch(() => undefined);
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadThreads]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(
    () => () => {
      shouldListenRef.current = false;
      recognitionRef.current?.stop();
    },
    []
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 192)}px`;
  };

  const toggleVoiceInput = async () => {
    if (shouldListenRef.current) {
      shouldListenRef.current = false;
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = (
      window as typeof window & {
        SpeechRecognition?: SpeechRecognitionConstructor;
        webkitSpeechRecognition?: SpeechRecognitionConstructor;
      }
    ).SpeechRecognition ||
      (
        window as typeof window & {
          webkitSpeechRecognition?: SpeechRecognitionConstructor;
        }
      ).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError(
        "Voice input is not supported by this browser. Please use Chrome or Edge."
      );
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setError(
        "Your browser cannot access a microphone. Please use the latest Chrome or Edge over HTTPS or localhost."
      );
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      setError(
        "Microphone permission is required. Allow microphone access in your browser settings and try again."
      );
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = voiceLanguage;
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      for (
        let index = event.resultIndex;
        index < event.results.length;
        index += 1
      ) {
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
        try {
          recognition.start();
        } catch {
          shouldListenRef.current = false;
          setIsListening(false);
          setError(
            "Voice recognition stopped unexpectedly. Please start it again."
          );
        }
      }, 150);
    };
    recognition.onerror = (event) => {
      if (event.error === "aborted" && !shouldListenRef.current) return;
      if (event.error === "no-speech") return;
      shouldListenRef.current = false;
      setIsListening(false);
      const voiceErrors: Record<string, string> = {
        "not-allowed":
          "Microphone permission was denied. Allow it in the browser address bar and try again.",
        "service-not-allowed":
          "Speech recognition is blocked by this browser or network.",
        "audio-capture": "No microphone was found. Connect one and try again.",
        "no-speech":
          "No speech was detected. Please speak clearly and try again.",
      };
      setError(
        voiceErrors[event.error] || "Voice recognition failed. Please try again."
      );
    };
    recognitionRef.current = recognition;
    setError(null);
    shouldListenRef.current = true;
    setIsListening(true);
    try {
      recognition.start();
    } catch {
      shouldListenRef.current = false;
      setIsListening(false);
      setError(
        "Voice recognition could not start. Please wait a moment and try again."
      );
    }
  };

  const sendMessage = async () => {
    if ((!input.trim() && !selectedFile) || isLoading || !session?.user) return;

    const userMessage = input.trim() || `Uploaded ${selectedFile?.name}`;
    setInput("");
    if (inputRef.current) inputRef.current.style.height = "auto";
    setSelectedFile(null);
    setIsLoading(true);
    setError(null);

    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      if (selectedFile) {
        const form = new FormData();
        form.append("file", selectedFile);
        form.append("message", input.trim());
        if (threadId) form.append("thread_id", threadId);
        form.append("attach_to_profile", "true");
        const response = await fetch(`${API_BASE}/api/v1/chat/upload`, {
          method: "POST",
          headers: authHeaders(),
          body: form,
        });
        if (!response.ok)
          throw new Error(`Upload failed: ${await response.text()}`);
        const data = await response.json();
        setMessages((previous) => [
          ...previous,
          {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.response,
            timestamp: new Date(),
            sources: data.retrieved_docs || [],
          },
        ]);
        if (data.thread_id) setThreadId(data.thread_id);
        await loadThreads();
        return;
      }

      const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeaders(),
        },
        body: JSON.stringify({
          message: userMessage,
          thread_id: threadId || undefined,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      if (!response.body) throw new Error("The server did not return a stream");

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let completed = false;

      while (!completed) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() || "";
        for (const event of events) {
          const dataLine = event
            .split("\n")
            .find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const eventData = JSON.parse(dataLine.slice(6));
          if (eventData.type === "token") {
            setMessages((previous) =>
              previous.map((item) =>
                item.id === assistantMessage.id
                  ? { ...item, content: item.content + eventData.content }
                  : item
              )
            );
          } else if (eventData.type === "done") {
            completed = true;
            setThreadId(eventData.thread_id);
            setMessages((previous) =>
              previous.map((item) =>
                item.id === assistantMessage.id
                  ? { ...item, sources: eventData.retrieved_docs || [] }
                  : item
              )
            );
            await loadThreads();
          } else if (eventData.type === "error") {
            throw new Error(eventData.detail || "Chat generation failed");
          }
        }
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `⚠️ ${errorMessage}. Please make sure the backend is running and Ollama is available at http://localhost:11434`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setThreadId("");
    setError(null);
    inputRef.current?.focus();
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="flex h-full flex-col bg-white dark:bg-[#08090E] text-gray-900 dark:text-[#F0F4FF] transition-colors duration-500">
      <div className="flex items-center justify-between border-b border-black/10 dark:border-white/8 px-4 sm:px-6 py-3 bg-white dark:bg-[#08090E] transition-colors duration-500">
        <div className="flex items-center gap-3 transition-colors duration-500">
          <div className="w-8 h-8 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0 transition-colors duration-500">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h1 className="font-syne text-sm font-extrabold tracking-tight text-gray-900 dark:text-[#F0F4FF] transition-colors duration-500">
              AI Chat Assistant
            </h1>
            <p className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280] tracking-wide transition-colors duration-500">
              Ollama + LangGraph • student copilot
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 transition-colors duration-500">
          <div className="relative">
            <select
              value={threadId}
              onChange={(event) => loadThread(event.target.value)}
              className="appearance-none max-w-44 border border-black/10 dark:border-white/8 bg-white dark:bg-[#0D0E16] font-mono text-[11px] text-gray-500 dark:text-[#6B7280] px-3 py-1.5 pr-7 focus:outline-none focus:border-[#0C65D2]/50 transition-colors duration-500"
              aria-label="Saved conversations"
            >
              <option value="">Conversations</option>
              {threads.map((thread) => (
                <option key={thread.id} value={thread.id}>
                  {thread.title}
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 h-3 w-3 text-gray-400 dark:text-[#6B7280] transition-colors duration-500" />
          </div>

          {threadId && (
            <span className="font-mono text-[10px] text-[#0C65D2] border border-[#0C65D2]/30 bg-[#0C65D2]/5 px-2 py-1 tracking-widest hidden sm:inline transition-colors duration-500">
              {threadId.slice(0, 8)}…
            </span>
          )}

          <button
            onClick={clearChat}
            disabled={messages.length === 0}
            className="flex items-center gap-1.5 font-mono text-[11px] text-gray-400 dark:text-[#6B7280] hover:text-gray-900 dark:hover:text-[#F0F4FF] border border-black/10 dark:border-white/8 hover:border-black/30 dark:hover:border-white/20 px-3 py-1.5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors duration-500"
          >
            <Trash2 className="h-3.5 w-3.5" />
            New Chat
          </button>
        </div>
      </div>

      {error && (
        <div className="border-b border-red-500/20 bg-red-500/5 px-4 py-2 flex items-center justify-between">
          <span className="font-mono text-[11px] text-red-500 flex items-center gap-2 transition-colors duration-500">
            <MessageSquare className="h-3.5 w-3.5 shrink-0" />
            {error}
          </span>
          <button
            onClick={() => setError(null)}
            className="text-red-400 hover:text-red-600 ml-4 shrink-0"
            aria-label="Dismiss error"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-5 transition-colors duration-500">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center transition-colors duration-500">
            <div className="w-12 h-12 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] mb-5 transition-colors duration-500">
              <MessageSquare className="h-5 w-5" />
            </div>
            <h3 className="font-syne text-lg font-extrabold text-gray-900 dark:text-[#F0F4FF] mb-2">
              Start a conversation
            </h3>
            <p className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280] max-w-sm leading-relaxed mb-6 transition-colors duration-500">
              Ask about scholarships, internships, eligibility, applications, or
              anything on your student journey.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {[
                { label: "Find Scholarships", q: "What scholarships am I eligible for?" },
                { label: "Internship Guide", q: "How do I apply for internships?" },
                { label: "Required Documents", q: "What documents do I need for applications?" },
                { label: "Eligibility Help", q: "Explain the eligibility criteria for merit scholarships" },
              ].map(({ label, q }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => setInput(q)}
                  className="flex items-center gap-1.5 font-mono text-[10px] text-gray-400 dark:text-[#6B7280] border border-black/10 dark:border-white/8 px-3 py-1.5 hover:border-[#0C65D2]/40 hover:text-[#0C65D2] transition-all duration-500"
                >
                  <Sparkles className="h-3 w-3" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onCopy={copyMessage}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {isLoading && (
          <div className="flex items-start gap-3 transition-colors duration-500">
            <div className="w-7 h-7 bg-[#0C65D2]/10 border border-[#0C65D2]/20 flex items-center justify-center text-[#0C65D2] shrink-0">
              <Bot className="h-3.5 w-3.5" />
            </div>
            <div className="flex items-center gap-2 px-4 py-3 border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0D0E16]">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-[#0C65D2]" />
              <span className="font-mono text-[11px] text-gray-400 dark:text-[#6B7280]">
                thinking…
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-black/10 dark:border-white/8 px-4 sm:px-6 py-4 bg-white dark:bg-[#08090E] transition-colors duration-500">
        <div className="max-w-4xl mx-auto">
          {selectedFile && (
            <div className="mb-2 flex w-fit items-center gap-2 border border-[#0C65D2]/30 bg-[#0C65D2]/5 px-3 py-1.5">
              <Paperclip className="h-3 w-3 text-[#0C65D2]" />
              <span className="font-mono text-[10px] text-[#0C65D2]">
                {selectedFile.name}
              </span>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                aria-label="Remove attachment"
                className="text-[#0C65D2]/60 hover:text-[#0C65D2] transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}

          <div className="flex items-end gap-2 transition-colors duration-500">
            <label
              className="flex h-9 w-9 shrink-0 cursor-pointer items-center justify-center border border-black/10 dark:border-white/8 text-gray-400 hover:border-[#0C65D2]/40 hover:text-[#0C65D2] transition-all duration-500"
              aria-label="Attach a document"
            >
              <Paperclip className="h-4 w-4" />
              <input
                type="file"
                className="sr-only"
                accept="image/*,.pdf"
                onChange={(event) =>
                  setSelectedFile(event.target.files?.[0] || null)
                }
                disabled={isLoading}
              />
            </label>

            <textarea
              ref={inputRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask about scholarships, internships, eligibility…"
              disabled={isLoading}
              rows={1}
              className="flex-1 min-h-9 max-h-48 px-4 py-2 bg-gray-50 dark:bg-[#0D0E16] border border-black/10 dark:border-white/8 font-mono text-sm text-gray-900 dark:text-[#F0F4FF] placeholder:text-gray-400 dark:placeholder:text-[#6B7280] resize-none focus:outline-none focus:border-[#0C65D2]/50 transition-colors duration-500"
              style={{ height: "36px" }}
            />

            <div className="relative">
              <select
                value={voiceLanguage}
                onChange={(event) => setVoiceLanguage(event.target.value)}
                disabled={isLoading || isListening}
                className="appearance-none h-9 border border-black/10 dark:border-white/8 bg-white dark:bg-[#0D0E16] font-mono text-[10px] text-gray-400 dark:text-[#6B7280] px-2 pr-5 focus:outline-none focus:border-[#0C65D2]/50 transition-colors duration-500"
                aria-label="Voice input language"
              >
                <option value="en-IN">EN</option>
                <option value="hi-IN">HI</option>
                <option value="mr-IN">MR</option>
              </select>
              <ChevronDown className="pointer-events-none absolute right-1 top-1/2 -translate-y-1/2 h-2.5 w-2.5 text-gray-400" />
            </div>

            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={isLoading}
              className={`flex h-9 w-9 shrink-0 items-center justify-center border transition-all duration-500 ${
                isListening
                  ? "border-red-500/40 bg-red-500/10 text-red-500"
                  : "border-black/10 dark:border-white/8 text-gray-400 hover:border-[#0C65D2]/40 hover:text-[#0C65D2]"
              }`}
              aria-label={isListening ? "Stop voice input" : "Start voice input"}
              title={
                isListening ? "Listening… click to stop" : "Speak your question"
              }
            >
              {isListening ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </button>

            <button
              onClick={sendMessage}
              disabled={
                (!input.trim() && !selectedFile) ||
                isLoading ||
                !session?.user
              }
              className="flex h-9 w-9 items-center justify-center bg-[#0C65D2] text-white hover:bg-[#0a52b0] disabled:opacity-30 disabled:cursor-not-allowed transition-colors duration-500"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>

          <p className="mt-2 font-mono text-[10px] text-center text-gray-400 dark:text-[#6B7280] transition-colors duration-500">
            <kbd className="px-1 py-0.5 border border-black/10 dark:border-white/8 text-[9px]">
              Enter
            </kbd>{" "}
            send ·{" "}
            <kbd className="px-1 py-0.5 border border-black/10 dark:border-white/8 text-[9px]">
              Shift+Enter
            </kbd>{" "}
            new line
          </p>
        </div>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: Message;
  onCopy: (content: string) => void;
}

function MessageBubble({ message, onCopy }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    onCopy(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} transition-colors duration-500`}
    >
      <div
        className={`w-7 h-7 shrink-0 flex items-center justify-center border ${
          isUser
            ? "border-black/10 dark:border-white/8 bg-gray-100 dark:bg-[#0D0E16] text-gray-400"
            : "border-[#0C65D2]/20 bg-[#0C65D2]/10 text-[#0C65D2]"
        }`}
      >
        {isUser ? (
          <User className="h-3.5 w-3.5" />
        ) : (
          <Bot className="h-3.5 w-3.5" />
        )}
      </div>

      <div className={`flex flex-col gap-1 max-w-[75%] ${isUser ? "items-end" : "items-start"} transition-colors duration-500`}>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0D0E16] px-3 py-2.5">
            <div className="flex items-center gap-1.5 font-mono text-[10px] text-gray-400 dark:text-[#6B7280] mb-2 tracking-widest uppercase">
              <Sparkles className="h-3 w-3 text-[#0C65D2]" />
              Sources ({message.sources.length})
            </div>
            <div className="space-y-1.5">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className="border border-black/10 dark:border-white/8 px-2.5 py-2 bg-white dark:bg-[#08090E]"
                >
                  <p className="font-mono text-[11px] text-gray-900 dark:text-[#F0F4FF] mb-1">
                    {source.title}
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    <Tag color="blue">{source.category}</Tag>
                    {source.relevance_score && (
                      <Tag color="green">
                        {(source.relevance_score * 100).toFixed(0)}% match
                      </Tag>
                    )}
                    {source.deadline && (
                      <Tag color="amber">Due {source.deadline}</Tag>
                    )}
                    {source.amount && (
                      <Tag color="blue">₹{source.amount.toLocaleString()}</Tag>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div
          className={`px-4 py-3 transition-colors duration-500 ${
            isUser
              ? "bg-[#0C65D2] text-white"
              : "border border-black/10 dark:border-white/8 bg-gray-50 dark:bg-[#0D0E16] text-gray-900 dark:text-[#F0F4FF]"
          }`}
        >
          <p className="font-mono text-sm leading-relaxed whitespace-pre-wrap m-0">
            {message.content}
          </p>
        </div>

        <div className="flex items-center gap-2 px-1">
          <span className="font-mono text-[10px] text-gray-400 dark:text-[#6B7280]">
            {formatTime(message.timestamp)}
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 font-mono text-[10px] text-gray-400 hover:text-gray-700 dark:hover:text-[#F0F4FF] transition-colors"
            aria-label={copied ? "Copied!" : "Copy message"}
          >
            {copied ? (
              <Check className="h-3 w-3 text-[#0C65D2]" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
            {copied && <span>Copied</span>}
          </button>
        </div>
      </div>
    </div>
  );
}

function Tag({
  color,
  children,
}: {
  color: "blue" | "green" | "amber";
  children: React.ReactNode;
}) {
  const styles = {
    blue: "border-[#0C65D2]/20 bg-[#0C65D2]/5 text-[#0C65D2]",
    green: "border-emerald-500/20 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400",
    amber: "border-amber-500/20 bg-amber-500/5 text-amber-600 dark:text-amber-400",
  };
  return (
    <span
      className={`font-mono text-[9px] border px-1.5 py-0.5 tracking-wide ${styles[color]}`}
    >
      {children}
    </span>
  );
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}