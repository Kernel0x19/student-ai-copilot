"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { Session } from "@supabase/supabase-js";
import { Send, MessageSquare, Bot, User, Loader2, Sparkles, Trash2, Copy, Check, Paperclip, X, Mic, MicOff } from "lucide-react";
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

  const authHeaders = useCallback(() => ({
    "X-User-Id": session?.user.id || "",
    "X-User-Email": session?.user.email || "",
  }), [session]);

  const loadThreads = useCallback(async () => {
    if (!session?.user) return;
    const response = await fetch(`${API_BASE}/api/v1/chat/threads`, { headers: authHeaders() });
    if (response.ok) {
      const data = await response.json();
      setThreads(data.threads || []);
    }
  }, [API_BASE, authHeaders, session]);

  const loadThread = async (selectedThreadId: string) => {
    if (!selectedThreadId) return;
    const response = await fetch(`${API_BASE}/api/v1/chat/history/${selectedThreadId}`, { headers: authHeaders() });
    if (!response.ok) return;
    const data = await response.json();
    setThreadId(selectedThreadId);
    setMessages(data.history.map((message: { role: "user" | "assistant"; content: string }, index: number) => ({
      id: `${selectedThreadId}-${index}`,
      role: message.role,
      content: message.content,
      timestamp: new Date(),
    })));
    setError(null);
  };

  // Keep the current Supabase session in sync without the deprecated
  // @supabase/auth-helpers-react package.
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
    // Defer the initial fetch until after this render commits.
    const timer = window.setTimeout(() => {
      loadThreads().catch(() => undefined);
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadThreads]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => () => {
    shouldListenRef.current = false;
    recognitionRef.current?.stop();
  }, []);

  const toggleVoiceInput = async () => {
    if (shouldListenRef.current) {
      shouldListenRef.current = false;
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    const SpeechRecognition = (window as typeof window & {
      SpeechRecognition?: SpeechRecognitionConstructor;
      webkitSpeechRecognition?: SpeechRecognitionConstructor;
    }).SpeechRecognition || (window as typeof window & {
      webkitSpeechRecognition?: SpeechRecognitionConstructor;
    }).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Voice input is not supported by this browser. Please use Chrome or Edge.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setError("Your browser cannot access a microphone. Please use the latest Chrome or Edge over HTTPS or localhost.");
      return;
    }
    try {
      // Trigger the browser permission prompt before beginning speech recognition.
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      setError("Microphone permission is required. Allow microphone access in your browser settings and try again.");
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
      // Browsers can end recognition after a pause even in continuous mode.
      // Restart until the student explicitly taps the microphone again.
      window.setTimeout(() => {
        if (!shouldListenRef.current) return;
        try {
          recognition.start();
        } catch {
          shouldListenRef.current = false;
          setIsListening(false);
          setError("Voice recognition stopped unexpectedly. Please start it again.");
        }
      }, 150);
    };
    recognition.onerror = (event) => {
      if (event.error === "aborted" && !shouldListenRef.current) return;
      if (event.error === "no-speech") return;
      shouldListenRef.current = false;
      setIsListening(false);
      const voiceErrors: Record<string, string> = {
        "not-allowed": "Microphone permission was denied. Allow it in the browser address bar and try again.",
        "service-not-allowed": "Speech recognition is blocked by this browser or network.",
        "audio-capture": "No microphone was found. Connect one and try again.",
        "no-speech": "No speech was detected. Please speak clearly and try again.",
      };
      setError(voiceErrors[event.error] || "Voice recognition failed. Please try again.");
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
      setError("Voice recognition could not start. Please wait a moment and try again.");
    }
  };

  const sendMessage = async () => {
    if ((!input.trim() && !selectedFile) || isLoading || !session?.user) return;

    const userMessage = input.trim() || `Uploaded ${selectedFile?.name}`;
    setInput("");
    setSelectedFile(null);
    setIsLoading(true);
    setError(null);

    // Add user message immediately
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
          method: "POST", headers: authHeaders(), body: form,
        });
        if (!response.ok) throw new Error(`Upload failed: ${await response.text()}`);
        const data = await response.json();
        setMessages((previous) => [...previous, {
          id: (Date.now() + 1).toString(), role: "assistant", content: data.response,
          timestamp: new Date(), sources: data.retrieved_docs || [],
        }]);
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
          const dataLine = event.split("\n").find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const eventData = JSON.parse(dataLine.slice(6));
          if (eventData.type === "token") {
            setMessages((previous) => previous.map((item) => item.id === assistantMessage.id
              ? { ...item, content: item.content + eventData.content }
              : item));
          } else if (eventData.type === "done") {
            completed = true;
            setThreadId(eventData.thread_id);
            setMessages((previous) => previous.map((item) => item.id === assistantMessage.id
              ? { ...item, sources: eventData.retrieved_docs || [] }
              : item));
            await loadThreads();
          } else if (eventData.type === "error") {
            throw new Error(eventData.detail || "Chat generation failed");
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message";
      setError(errorMessage);

      // Add error message to chat
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
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4 bg-card">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">AI Chat Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Powered by Ollama + LangGraph • Your student success copilot
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={threadId}
            onChange={(event) => loadThread(event.target.value)}
            className="max-w-44 rounded-lg border bg-background px-2 py-1.5 text-sm"
            aria-label="Saved conversations"
          >
            <option value="">Saved conversations</option>
            {threads.map((thread) => <option key={thread.id} value={thread.id}>{thread.title}</option>)}
          </select>
          {threadId && (
            <span className="px-2 py-1 text-xs bg-muted rounded-full font-mono">
              Thread: {threadId.slice(0, 8)}...
            </span>
          )}
          <button
            onClick={clearChat}
            disabled={messages.length === 0}
            className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            New Chat
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="border-y border-destructive/20 bg-destructive/5 px-4 py-2 flex items-center justify-between">
          <span className="text-sm text-destructive flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            {error}
          </span>
          <button
            onClick={() => setError(null)}
            className="text-destructive hover:text-destructive/80"
          >
            ✕
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <MessageSquare className="h-16 w-16 mb-4 opacity-30" />
            <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
            <p className="max-w-md text-sm">
              Ask me about scholarships, internships, eligibility, applications,
              or anything related to your student journey!
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              <SuggestionChip onClick={() => setInput("What scholarships am I eligible for?")}>
                <Sparkles className="h-3 w-3 mr-1" />
                Find Scholarships
              </SuggestionChip>
              <SuggestionChip onClick={() => setInput("How do I apply for internships?")}>
                <Sparkles className="h-3 w-3 mr-1" />
                Internship Guide
              </SuggestionChip>
              <SuggestionChip onClick={() => setInput("What documents do I need for applications?")}>
                <Sparkles className="h-3 w-3 mr-1" />
                Required Documents
              </SuggestionChip>
              <SuggestionChip onClick={() => setInput("Explain the eligibility criteria for merit scholarships")}>
                <Sparkles className="h-3 w-3 mr-1" />
                Eligibility Help
              </SuggestionChip>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onCopy={copyMessage}
                showSources={message.id === messages.find((item) => item.role === "assistant" && item.sources?.length)?.id}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {/* Typing Indicator */}
        {isLoading && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1 px-4 py-3 bg-muted rounded-2xl rounded-bl-sm">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">AI is thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t p-4 bg-card">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end gap-2">
            <label className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-xl border hover:bg-accent" aria-label="Attach a document">
              <Paperclip className="h-5 w-5" />
              <input type="file" className="sr-only" accept="image/*,.pdf" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} disabled={isLoading} />
            </label>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about scholarships, internships, eligibility, applications..."
              disabled={isLoading}
              className="flex-1 min-h-[44px] max-h-48 px-4 py-3 bg-background border rounded-2xl resize-none focus-visible:ring-2 focus-visible:ring-ring transition-shadow"
              rows={1}
            />
            <select
              value={voiceLanguage}
              onChange={(event) => setVoiceLanguage(event.target.value)}
              disabled={isLoading || isListening}
              className="h-10 rounded-xl border bg-background px-2 text-xs"
              aria-label="Voice input language"
            >
              <option value="en-IN">English</option>
              <option value="hi-IN">हिन्दी</option>
              <option value="mr-IN">मराठी</option>
            </select>
            <button
              type="button"
              onClick={toggleVoiceInput}
              disabled={isLoading}
              className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border transition-colors ${isListening ? "bg-destructive text-destructive-foreground" : "hover:bg-accent"}`}
              aria-label={isListening ? "Stop voice input" : "Start voice input"}
              title={isListening ? "Listening… click to stop" : "Speak your question"}
            >
              {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>
            <button
              onClick={sendMessage}
              disabled={(!input.trim() && !selectedFile) || isLoading || !session?.user}
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Send message"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
          {selectedFile && (
            <div className="mt-2 flex w-fit items-center gap-2 rounded-lg bg-muted px-3 py-1.5 text-xs">
              <Paperclip className="h-3.5 w-3.5" /> {selectedFile.name}
              <button type="button" onClick={() => setSelectedFile(null)} aria-label="Remove attachment"><X className="h-3.5 w-3.5" /></button>
            </div>
          )}
          <p className="mt-2 text-xs text-center text-muted-foreground">
            Press <kbd className="px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono">Enter</kbd> to send,
            <kbd className="px-1.5 py-0.5 bg-muted rounded text-[10px] font-mono ml-1">Shift+Enter</kbd> for new line. Select a language, then use the microphone to dictate.
          </p>
        </div>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: Message;
  onCopy: (content: string) => void;
  showSources: boolean;
}

function MessageBubble({ message, onCopy, showSources }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`flex gap-3 animate-fade-in ${
        message.role === "user" ? "justify-end" : "justify-start"
      }`}
    >
      {message.role === "assistant" && (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary shrink-0">
          <Bot className="h-4 w-4" />
        </div>
      )}
      {message.role === "user" && (
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted shrink-0">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
      )}

      <div
        className={`max-w-[75%] ${
          message.role === "user"
            ? "rounded-2xl rounded-tr-sm bg-primary text-primary-foreground"
            : "rounded-2xl rounded-tl-sm bg-muted"
        } flex flex-col`}
      >
        <div className="order-2 px-4 py-3 prose prose-sm dark:prose-invert max-w-none">
          <p className="whitespace-pre-wrap m-0">{message.content}</p>
        </div>

        {/* Sources */}
        {showSources && message.sources && message.sources.length > 0 && (
          <div className="order-1 px-4 pb-3 pt-3 border-b border-border/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
              <Sparkles className="h-3 w-3" />
              <span className="font-medium">Sources ({message.sources.length})</span>
            </div>
            <div className="space-y-1">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className="px-3 py-2 bg-background/50 rounded-lg text-xs border border-border/50"
                >
                  <div className="font-medium text-foreground">{source.title}</div>
                  <div className="flex flex-wrap gap-2 mt-1 text-muted-foreground">
                    <span className="px-1.5 py-0.5 bg-primary/10 text-primary rounded text-[10px]">
                      {source.category}
                    </span>
                    {source.relevance_score && (
                      <span className="px-1.5 py-0.5 bg-green/10 text-green rounded text-[10px]">
                        Relevance: {(source.relevance_score * 100).toFixed(0)}%
                      </span>
                    )}
                    {source.deadline && (
                      <span className="px-1.5 py-0.5 bg-orange/10 text-orange rounded text-[10px]">
                        Deadline: {source.deadline}
                      </span>
                    )}
                    {source.amount && (
                      <span className="px-1.5 py-0.5 bg-blue/10 text-blue rounded text-[10px]">
                        ₹{source.amount.toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timestamp and Actions */}
        <div className="order-3 flex items-center justify-end gap-2 px-4 pb-2 text-[10px] text-muted-foreground">
          <span>{formatTime(message.timestamp)}</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 p-1 rounded hover:bg-background/50 transition-colors"
            aria-label={copied ? "Copied!" : "Copy message"}
          >
            {copied ? (
              <Check className="h-3 w-3 text-green" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
            {copied && <span className="text-[10px]">Copied!</span>}
          </button>
        </div>
      </div>
    </div>
  );
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

interface SuggestionChipProps {
  children: React.ReactNode;
  onClick: () => void;
}

function SuggestionChip({ children, onClick }: SuggestionChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="px-3 py-1.5 text-xs bg-muted hover:bg-muted/80 text-muted-foreground hover:text-foreground rounded-full border border-border transition-colors"
    >
      {children}
    </button>
  );
}
