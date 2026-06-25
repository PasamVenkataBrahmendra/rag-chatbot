import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import axios from "axios";

const API = "http://localhost:8000";

// ── THEMES ─────────────────────────────────────────────────
const THEMES = {
  dark: {
    bg: "#0a0a0f",
    bg2: "#111118",
    sidebar: "#0d0d15",
    text: "#f0f0ff",
    text2: "#8888aa",
    border: "rgba(99,102,241,0.15)",
    input: "rgba(255,255,255,0.05)",
    userBubble: "rgba(99,102,241,0.2)",
    botBubble: "rgba(255,255,255,0.04)",
    hover: "rgba(255,255,255,0.05)",
    card: "rgba(255,255,255,0.03)"
  },
  light: {
    bg: "#f8f9ff",
    bg2: "#ffffff",
    sidebar: "#f0f0fa",
    text: "#1a1a2e",
    text2: "#666680",
    border: "rgba(99,102,241,0.2)",
    input: "rgba(99,102,241,0.05)",
    userBubble: "rgba(99,102,241,0.15)",
    botBubble: "#ffffff",
    hover: "rgba(99,102,241,0.05)",
    card: "#ffffff"
  }
};

// ── FEATURES ───────────────────────────────────────────────
const FEATURES = [
  { id: "chat", icon: "💬", label: "Chat", color: "#6366f1", desc: "Ask anything" },
  { id: "search", icon: "🔍", label: "Web Search", color: "#10b981", desc: "Live internet" },
  { id: "image", icon: "🖼️", label: "Image Gen", color: "#f59e0b", desc: "Create images" },
  { id: "pdf", icon: "📄", label: "PDF Chat", color: "#06b6d4", desc: "Chat with docs" },
  { id: "code", icon: "💻", label: "Code", color: "#8b5cf6", desc: "Write & run" },
  { id: "math", icon: "🧮", label: "Math", color: "#ec4899", desc: "Step by step" },
  { id: "research", icon: "📊", label: "Research", color: "#6366f1", desc: "Full reports" },
  { id: "tutor", icon: "🎓", label: "Tutor", color: "#10b981", desc: "Learn anything" },
  { id: "resume", icon: "📋", label: "Resume", color: "#f59e0b", desc: "Analyze CV" },
  { id: "email", icon: "📧", label: "Email", color: "#06b6d4", desc: "Write emails" },
  { id: "sql", icon: "🗄️", label: "SQL", color: "#8b5cf6", desc: "Text to SQL" },
  { id: "debate", icon: "⚔️", label: "Debate", color: "#ec4899", desc: "Both sides" }
];

const LANGUAGES = [
  "English", "Hindi", "Spanish", "French", "German",
  "Arabic", "Chinese", "Japanese", "Portuguese", "Telugu", "Tamil"
];
// ── YOUTUBE TRANSLATOR PLAYER ──────────────────────────────
function YouTubePlayer({ videoId, translation, targetLang, theme, onClose }) {
  const [speaking, setSpeaking] = useState(false);
  const utteranceRef = useRef(null);

  const speakTranslation = () => {
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(translation.slice(0, 2000));
    const langMap = {
      "Hindi": "hi-IN", "Telugu": "te-IN", "Tamil": "ta-IN",
      "Spanish": "es-ES", "French": "fr-FR", "German": "de-DE",
      "English": "en-US", "Japanese": "ja-JP", "Arabic": "ar-SA",
      "Chinese": "zh-CN", "Portuguese": "pt-BR",
      "Kannada": "kn-IN", "Malayalam": "ml-IN",
      "Marathi": "mr-IN", "Bengali": "bn-IN"
    };
    utterance.lang = langMap[targetLang] || "en-US";
    utterance.rate = 0.85;
    utterance.onend = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  };

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(0,0,0,0.85)",
      backdropFilter: "blur(10px)",
      zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: "20px"
    }}>
      <div style={{
        width: "100%", maxWidth: "960px",
        background: theme.bg2,
        borderRadius: "20px",
        border: `1px solid ${theme.border}`,
        overflow: "hidden",
        boxShadow: "0 30px 60px rgba(0,0,0,0.5)"
      }}>
        {/* Header */}
        <div style={{
          padding: "14px 20px",
          borderBottom: `1px solid ${theme.border}`,
          display: "flex", alignItems: "center", gap: "12px",
          background: "rgba(99,102,241,0.05)"
        }}>
          <span style={{ fontSize: "22px" }}>🎬</span>
          <div>
            <div style={{ fontWeight: "700", fontSize: "15px", color: theme.text }}>
              YouTube Translator
            </div>
            <div style={{ fontSize: "11px", color: theme.text2 }}>
              Watching in original • Audio available in {targetLang}
            </div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
            <button
              onClick={speakTranslation}
              style={{
                padding: "8px 18px",
                background: speaking
                  ? "rgba(239,68,68,0.2)"
                  : "linear-gradient(135deg, #6366f1, #06b6d4)",
                border: `1px solid ${speaking ? "rgba(239,68,68,0.4)" : "transparent"}`,
                borderRadius: "8px",
                color: speaking ? "#ef4444" : "white",
                cursor: "pointer", fontSize: "13px", fontWeight: "600",
                display: "flex", alignItems: "center", gap: "6px"
              }}
            >
              {speaking ? "⏹️ Stop Audio" : `🔊 Play in ${targetLang}`}
            </button>
            <button
              onClick={() => {
  if (speaking) {
    window.speechSynthesis.cancel();
    setSpeaking(false);
    return;
  }

  if (!translation || !translation.trim()) {
    alert("Translation not available");
    return;
  }

  const utterance =
    new SpeechSynthesisUtterance(
      translation
    );

  utteranceRef.current = utterance;

  utterance.lang =
    targetLang === "Telugu"
      ? "te-IN"
      : targetLang === "Hindi"
      ? "hi-IN"
      : "en-US";

  utterance.rate = 1;

  utterance.onstart = () => {
    setSpeaking(true);
  };

  utterance.onend = () => {
    setSpeaking(false);
  };

  utterance.onerror = (e) => {
    console.log("Speech error", e);
    setSpeaking(false);
  };

  window.speechSynthesis.cancel();

  setTimeout(() => {
    window.speechSynthesis.speak(
      
      utterance
    );
  }, 150);
}}
            >✕ Close</button>
          </div>
        </div>

        {/* Video + Translation */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr" }}>
          {/* YouTube embed */}
          <div style={{ position: "relative", paddingBottom: "56.25%", height: 0 }}>
            <iframe
              style={{
                position: "absolute", top: 0, left: 0,
                width: "100%", height: "100%", border: "none"
              }}
              src={`https://www.youtube.com/embed/${videoId}`}
              title="YouTube video"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>

          {/* Translation text */}
          <div style={{
            padding: "20px",
            background: theme.bg,
            borderLeft: `1px solid ${theme.border}`,
            overflow: "auto",
            maxHeight: "400px"
          }}>
            <div style={{
              fontSize: "10px", color: "#6366f1",
              textTransform: "uppercase", letterSpacing: "0.8px",
              marginBottom: "12px", fontWeight: "700"
            }}>
              📝 {targetLang} Translation
            </div>
            <div
            style={{
            whiteSpace: "pre-wrap",
            padding: "16px",
            overflowY: "auto",
            height: "100%",
          }}
          >
          {translation?.trim()
          ? translation
          : "Translation not available yet..."}
          </div>   
                                   
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: "10px 20px",
          borderTop: `1px solid ${theme.border}`,
          background: "rgba(99,102,241,0.03)",
          fontSize: "11px", color: theme.text2,
          display: "flex", gap: "20px", alignItems: "center"
        }}>
          <span>▶️ Play the video on the left</span>
          <span>🔊 Click "Play in {targetLang}" to hear translated audio</span>
          <span>📖 Read translation on the right panel</span>
        </div>
      </div>
    </div>
  );
}

// ── TYPING INDICATOR ───────────────────────────────────────
function TypingDots({ theme }) {
  return (
    <div style={{
      display: "flex", gap: "5px", padding: "14px 18px",
      background: theme.botBubble,
      borderRadius: "18px 18px 18px 4px",
      border: `1px solid ${theme.border}`,
      width: "fit-content"
    }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: "7px", height: "7px", borderRadius: "50%",
          background: "#6366f1",
          animation: `typingDot 1.2s ease-in-out ${i * 0.2}s infinite`
        }} />
      ))}
    </div>
  );
}

// ── MESSAGE ────────────────────────────────────────────────
function Message({ msg, theme, onOpenPlayer }) {
  const isUser = msg.role === "user";

  return (
    <div style={{ marginBottom: "16px", animation: "msgIn 0.3s ease" }}>

      {/* Auto detected badge for user messages */}
      {isUser && msg.detectedMode && (() => {
        const modeInfo = FEATURES.find(f => f.id === msg.detectedMode);
        return (
          <div style={{
            display: "flex", justifyContent: "flex-end",
            marginBottom: "4px"
          }}>
            <span style={{
              fontSize: "10px",
              color: modeInfo?.color || "#6366f1",
              fontWeight: "600",
              background: `${modeInfo?.color || "#6366f1"}15`,
              border: `1px solid ${modeInfo?.color || "#6366f1"}30`,
              padding: "2px 8px", borderRadius: "20px",
              display: "flex", alignItems: "center", gap: "4px"
            }}>
              ✨ Auto-detected: {modeInfo?.icon} {modeInfo?.label}
            </span>
          </div>
        );
      })()}

      <div style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        gap: "10px", alignItems: "flex-start"
      }}>
        {!isUser && (
          <div style={{
            width: "34px", height: "34px", borderRadius: "50%",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "16px", flexShrink: 0, marginTop: "2px"
          }}>🤖</div>
        )}

        <div style={{ maxWidth: "78%" }}>
          <div style={{
            padding: "13px 18px",
            borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
            background: isUser
              ? "linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2))"
              : theme.botBubble,
            border: `1px solid ${isUser ? "rgba(99,102,241,0.3)" : theme.border}`,
            color: theme.text,
            fontSize: "14px", lineHeight: "1.65"
          }}>
            {/* Generated image */}
            {msg.image && (
              <img
                src={`data:image/jpeg;base64,${msg.image}`}
                style={{ width: "100%", borderRadius: "10px", marginBottom: "10px" }}
                alt="generated"
              />
            )}

            {/* Message content */}
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{ borderRadius: "8px", margin: "8px 0", fontSize: "12px" }}
                      {...props}
                    >{String(children).replace(/\n$/, "")}</SyntaxHighlighter>
                  ) : (
                    <code style={{
                      background: "rgba(99,102,241,0.15)",
                      padding: "2px 6px", borderRadius: "4px", fontSize: "12px"
                    }} {...props}>{children}</code>
                  );
                }
              }}
            >{msg.content}</ReactMarkdown>

            {/* YouTube Player Button */}
            {msg.showPlayerButton && (
              <button
                onClick={() => {
                  onOpenPlayer(msg.videoId, msg.translationText, msg.translatedLang);
                }}
                style={{
                  marginTop: "12px",
                  padding: "10px 20px",
                  background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                  border: "none", borderRadius: "10px",
                  color: "white", cursor: "pointer",
                  fontSize: "14px", fontWeight: "600",
                  display: "flex", alignItems: "center", gap: "8px"
                }}
              >
                🎬 Open YouTube Player
              </button>
            )}

            {/* Code execution output */}
            {msg.execution_output && (
              <div style={{
                marginTop: "10px", padding: "10px 12px",
                background: msg.execution_success ? "#0d1117" : "#1a0505",
                borderRadius: "8px", fontFamily: "monospace", fontSize: "12px",
                color: msg.execution_success ? "#00ff88" : "#ff6b6b",
                border: `1px solid ${msg.execution_success ? "#00ff8830" : "#ff6b6b30"}`
              }}>
                {msg.execution_success ? "▶ Output:" : "❌ Error:"} {msg.execution_output}
              </div>
            )}
          </div>

          {/* Source and confidence */}
          {msg.source && (
            <div style={{
              marginTop: "5px", fontSize: "11px",
              color: theme.text2, paddingLeft: "4px",
              display: "flex", gap: "8px", alignItems: "center"
            }}>
              <span>📚 {msg.source}</span>
              {msg.confidence && (
                <span style={{
                  background: msg.confidence >= 80
                    ? "rgba(16,185,129,0.15)"
                    : "rgba(245,158,11,0.15)",
                  color: msg.confidence >= 80 ? "#10b981" : "#f59e0b",
                  padding: "1px 7px", borderRadius: "10px", fontSize: "10px"
                }}>{msg.confidence}%</span>
              )}
            </div>
          )}
        </div>

        {isUser && (
          <div style={{
            width: "34px", height: "34px", borderRadius: "50%",
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "16px", flexShrink: 0, marginTop: "2px"
          }}>🧑</div>
        )}

      </div>
    </div>
  );
}

// ── SIDEBAR ────────────────────────────────────────────────
function Sidebar({
  theme, isDark, setIsDark, mode, setMode,
  sessions, currentSession,
  onNewChat, onLoadSession, onDeleteSession,
  language, setLanguage, sidebarOpen
}) {
  if (!sidebarOpen) return null;

  return (
    <div style={{
      width: "240px", flexShrink: 0,
      background: theme.sidebar,
      borderRight: `1px solid ${theme.border}`,
      display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden"
    }}>
      {/* Logo */}
      <div style={{ padding: "16px", borderBottom: `1px solid ${theme.border}` }}>
        <div style={{
          display: "flex", alignItems: "center",
          gap: "10px", marginBottom: "12px"
        }}>
          <div style={{
            width: "36px", height: "36px", borderRadius: "10px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: "18px"
          }}>🤖</div>
          <span style={{
            fontWeight: "800", fontSize: "18px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>PVBotX</span>

          {/* Theme toggle in sidebar */}
          <div style={{
            marginLeft: "auto",
            display: "flex",
            background: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)",
            borderRadius: "50px", padding: "2px",
            border: `1px solid ${theme.border}`
          }}>
            <button
              onClick={() => setIsDark(false)}
              style={{
                padding: "3px 8px", borderRadius: "50px", border: "none",
                background: !isDark ? "white" : "transparent",
                color: !isDark ? "#1a1a2e" : theme.text2,
                cursor: "pointer", fontSize: "11px", fontWeight: "600",
                transition: "all 0.3s"
              }}
            >☀️</button>
            <button
              onClick={() => setIsDark(true)}
              style={{
                padding: "3px 8px", borderRadius: "50px", border: "none",
                background: isDark ? "#1a1a2e" : "transparent",
                color: isDark ? "white" : theme.text2,
                cursor: "pointer", fontSize: "11px", fontWeight: "600",
                transition: "all 0.3s"
              }}
            >🌙</button>
          </div>
        </div>

        <button
          onClick={onNewChat}
          style={{
            width: "100%", padding: "8px",
            background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1))",
            border: "1px solid rgba(99,102,241,0.3)",
            borderRadius: "8px", color: theme.text,
            cursor: "pointer", fontSize: "13px", fontWeight: "500"
          }}
        >✏️ New Chat</button>
      </div>

      {/* Language */}
      <div style={{ padding: "10px 14px", borderBottom: `1px solid ${theme.border}` }}>
        <div style={{
          fontSize: "10px", color: theme.text2,
          marginBottom: "5px", textTransform: "uppercase", letterSpacing: "0.5px"
        }}>Language</div>
        <select
          value={language}
          onChange={e => setLanguage(e.target.value)}
          style={{
            width: "100%", padding: "5px 8px",
            background: theme.input,
            border: `1px solid ${theme.border}`,
            borderRadius: "6px", color: theme.text,
            fontSize: "12px", cursor: "pointer"
          }}
        >
          {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      {/* Smart Mode Info */}
      <div style={{ padding: "10px 14px", borderBottom: `1px solid ${theme.border}` }}>
        <div style={{
          padding: "10px 12px",
          background: "rgba(99,102,241,0.08)",
          border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: "8px",
          fontSize: "11px", color: theme.text2,
          lineHeight: "1.5"
        }}>
          <div style={{ color: "#6366f1", fontWeight: "600", marginBottom: "4px" }}>
            ✨ Smart Auto-Detection
          </div>
          Just type naturally! PVBotX detects what you need automatically.
        </div>
      </div>

      
      {/* Chat History */}
      <div style={{ flex: 1, overflow: "auto", padding: "10px" }}>
        <div style={{
          fontSize: "10px", color: theme.text2,
          padding: "0 4px 6px",
          textTransform: "uppercase", letterSpacing: "0.5px"
        }}>History</div>
        {sessions.slice(0, 10).map(s => (
          <div key={s.id} style={{ display: "flex", alignItems: "center", marginBottom: "2px" }}>
            <button
              onClick={() => onLoadSession(s.id)}
              style={{
                flex: 1, padding: "6px 8px",
                background: currentSession === s.id ? theme.hover : "transparent",
                border: "none", borderRadius: "6px",
                color: theme.text2, cursor: "pointer",
                fontSize: "11px", textAlign: "left",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
              }}
            >💬 {s.name}</button>
            <button
              onClick={() => onDeleteSession(s.id)}
              style={{
                background: "none", border: "none",
                color: theme.text2, cursor: "pointer",
                fontSize: "13px", padding: "0 4px", opacity: 0.4
              }}
            >×</button>
          </div>
        ))}

      </div>
    </div>
  );
}

// ── WELCOME SCREEN ─────────────────────────────────────────
const EXAMPLES = [
  { text: "Generate an image of a futuristic city on Mars", icon: "🖼️" },
  { text: "Search for latest AI news today", icon: "🔍" },
  { text: "Write Python code to sort a dictionary by value", icon: "💻" },
  { text: "Solve x² - 5x + 6 = 0 step by step", icon: "🧮" },
  { text: "What is machine learning?", icon: "💬" },
  { text: "Research report on quantum computing", icon: "📊" }
];

function WelcomeScreen({ theme, isDark, onExample }) {
  return (
    <div style={{
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      height: "100%", textAlign: "center", padding: "40px 20px"
    }}>
      <div style={{
        fontSize: "64px", marginBottom: "20px",
        animation: "float 4s ease-in-out infinite"
      }}>🤖</div>
      <h2 style={{
        fontSize: "28px", fontWeight: "800",
        marginBottom: "8px", color: theme.text,
        background: "linear-gradient(135deg, #6366f1, #06b6d4)",
        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
      }}>Welcome to PVBotX</h2>
      <p style={{
        color: theme.text2, fontSize: "15px",
        maxWidth: "480px", lineHeight: "1.6", marginBottom: "40px"
      }}>
        Just type naturally — I automatically detect if you want to
        search, generate images, write code, solve math or just chat.
      </p>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "12px", maxWidth: "700px", width: "100%"
      }}>
        {EXAMPLES.map((ex, i) => (
          <button
            key={i}
            onClick={() => onExample(ex.text)}
            style={{
              padding: "12px 16px",
              background: isDark ? "rgba(255,255,255,0.03)" : "rgba(99,102,241,0.04)",
              border: `1px solid ${theme.border}`,
              borderRadius: "12px",
              color: theme.text, cursor: "pointer",
              fontSize: "13px", textAlign: "left",
              display: "flex", alignItems: "center", gap: "10px",
              transition: "all 0.2s"
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = "rgba(99,102,241,0.4)";
              e.currentTarget.style.background = isDark
                ? "rgba(99,102,241,0.08)"
                : "rgba(99,102,241,0.08)";
              e.currentTarget.style.transform = "translateY(-2px)";
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = theme.border;
              e.currentTarget.style.background = isDark
                ? "rgba(255,255,255,0.03)"
                : "rgba(99,102,241,0.04)";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            <span style={{ fontSize: "20px" }}>{ex.icon}</span>
            <span style={{ lineHeight: "1.4" }}>{ex.text}</span>
          </button>
        ))}

      </div>
    </div>
  );
}



// ── MAIN CHAT APP ──────────────────────────────────────────
export default function ChatApp() {
  const [isDark, setIsDark] = useState(true);
  const [mode, setMode] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("English");
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [pdfName, setPdfName] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [currentYoutubeId, setCurrentYoutubeId] = useState(null);
  const [showYoutubePlayer, setShowYoutubePlayer] = useState(false);
  const [youtubeTranslation, setYoutubeTranslation] = useState("");
  const [targetLang, setTargetLang] = useState("");
  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);
  

  const startVoiceInput = () => {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Voice input not supported. Use Chrome.");
    return;
  }

  const recognition = new SpeechRecognition();

  recognitionRef.current = recognition;

  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.lang = "en-US"; // change if needed

  setIsRecording(true);

  recognition.onstart = () => {
    console.log("Recording started");
  };

  recognition.onresult = (event) => {
    let transcript = "";

    for (let i = 0; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }

    console.log("Voice:", transcript);

    setInput(transcript);

    if (textareaRef?.current) {
      textareaRef.current.value = transcript;
    }
  };

  recognition.onerror = (e) => {
    console.log("Speech error:", e);
    setIsRecording(false);
  };

  recognition.onend = () => {
    setIsRecording(false);
  };

  recognition.start();
};

const stopVoiceInput = () => {
  if (recognitionRef.current) {
    recognitionRef.current.stop();
  }
};

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  

  const theme = isDark ? THEMES.dark : THEMES.light;

  useEffect(() => { loadSessions(); }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const loadSessions = async () => {
    try {
      const res = await axios.get(`${API}/api/sessions`);
      setSessions(res.data);
    } catch (e) {}
  };

  const newChat = async () => {
    try {
      const res = await axios.post(`${API}/api/sessions`,
        new URLSearchParams({ name: "New Chat" })
      );
      setCurrentSession(res.data.id);
    } catch (e) {}
    setMessages([]);
    setMode("chat");
  };

  const loadSession = async (id) => {
    try {
      const res = await axios.get(`${API}/api/sessions/${id}/messages`);
      setMessages(res.data.map(m => ({ role: m.role, content: m.content })));
      setCurrentSession(id);
    } catch (e) {}
  };

  const deleteSession = async (id) => {
    try {
      await axios.delete(`${API}/api/sessions/${id}`);
      if (currentSession === id) { setMessages([]); setCurrentSession(null); }
      loadSessions();
    } catch (e) {}
  };

  const streamResponse = async (url, formData, onDelta, onDone) => {
    const response = await fetch(url, { method: "POST", body: formData });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      for (const line of chunk.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "delta") onDelta(data.content);
          else if (data.type === "done") onDone && onDone(data);
          else if (data.type === "execution") {
            onDone && onDone({ execution: true, success: data.success, output: data.output });
          }
        } catch (e) {}
      }
    }
  };

  const addBot = (content = "") => {
    setMessages(prev => [...prev, { role: "assistant", content }]);
    return (update) => {
      setMessages(prev => {
        const msgs = [...prev];
        msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], ...update };
        return msgs;
      });
    };
  };
  const uploadPDF = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API}/api/upload-pdf`, formData);
      if (res.data.success) {
        setPdfUploaded(true);
        setPdfName(res.data.filename);
        const update = addBot("");
        update({
          content: `✅ **${res.data.filename}** loaded! (${res.data.chunks} chunks)\n\nAsk me anything about this PDF and I'll answer with page citations.`
        });
      }
    } catch (e) {
      const update = addBot("");
      update({ content: "❌ Failed to upload PDF. Make sure the Flask API is running." });
    }
  };

  // ── AUTO DETECTION ─────────────────────────────────────
  const detectMode = (text) => {
    if (mode !== "chat") return mode;

    const t = text.toLowerCase().trim();

    // WhatsApp style greetings in any language
    const greetings = [
      "hlo", "hii", "heyy", "heyyy", "sup", "wassup", "wsp",
      "emchesthunavu", "emchestunnav", "ela unnav", "ela unav",
      "enti", "baagunnara", "bagunnaara", "namaste", "namasthe",
      "vanakkam", "sat sri akal", "kem cho", "kasa kay",
      "kemon acho", "ki khobor", "assalamualaikum", "salam"
    ];
    if (greetings.some(g => t.includes(g)) || t.length < 6) return "chat";

    // YouTube link detection
    if (/youtube\.com\/watch|youtu\.be\//i.test(text)) return "youtube_translate";

    // Image generation
    if (/generate.*image|create.*image|draw|paint|picture of|photo of|make.*image|image of/i.test(text)) return "image";

    // Web search
    if (/search|latest news|current.*price|today.*news|who won|what happened|breaking|live score/i.test(text)) return "search";

    // Code
    if (/write.*code|fix.*code|debug|python |javascript |java |function |class |algorithm|def |import |const |var /i.test(text)) return "code";

    // Math
    if (/solve|calculate|integral|derivative|equation|algebra|geometry|\d+\s*[\+\-\*\/\^]\s*\d+|find x/i.test(text)) return "math";

    // Research
    if (/research report|write.*report|comprehensive.*analysis|full report|in depth/i.test(text)) return "research";

    // Tutor
    if (/teach me|tutor|explain.*step by step|learn about|course on/i.test(text)) return "tutor";

    // Email
    if (/write.*email|draft.*email|email to|professional email/i.test(text)) return "email";

    // SQL
    if (/sql|database query|select.*from|insert into|create table/i.test(text)) return "sql";

    // Debate
    if (/debate|pros and cons|argue|for and against|both sides/i.test(text)) return "debate";

    // PDF
    if (/pdf|document|uploaded|in the file|from the doc/i.test(text) && pdfUploaded) return "pdf";

    return "chat";
  };

  // ── SEND MESSAGE ───────────────────────────────────────
  const sendMessage = async (text = input) => {
    if (!text.trim() || loading) return;
    // Check if user is replying with language for YouTube translation
    if (currentYoutubeId && /^(hindi|telugu|tamil|english|spanish|french|german|arabic|chinese|japanese|portuguese|kannada|malayalam|marathi|bengali|gujarati|urdu)$/i.test(text.trim())) {
      const selectedLang = text.trim().charAt(0).toUpperCase() + text.trim().slice(1).toLowerCase();
      setTargetLang(selectedLang);

      setMessages(prev => [...prev, { role: "user", content: text }]);
      setLoading(true);

      const update = addBot(`🔄 Fetching transcript and translating to ${selectedLang}...`);

      try {
        // Get YouTube transcript via Flask API
        const fd=new FormData();

fd.append(
 "video_id",
 currentYoutubeId
);

fd.append(
 "language",
 selectedLang
);

const res=
await axios.post(
 `${API}/api/youtube-translate`,
 fd
);

setYoutubeTranslation(
 res.data.translation
);

update({
 content:
 `✅ Translation ready`,
 showPlayerButton:true,
 videoId:currentYoutubeId,
 translatedLang:selectedLang,
 translationText:
 res.data.translation
});

      } catch (e) {
        update({ content: `❌ Translation failed: ${e.message}` });
      }

      setCurrentYoutubeId(null);
      setLoading(false);
      return;
    }


    setInput("");
    setLoading(true);

    const detectedMode = detectMode(text);
    const wasAutoDetected = detectedMode !== "chat" && mode === "chat";

    setMessages(prev => [...prev, {
      role: "user",
      content: text,
      detectedMode: wasAutoDetected ? detectedMode : null
    }]);

    try {
      const fd = new FormData();

      // ── YOUTUBE TRANSLATE ─────────────────────────────
      if (detectedMode === "youtube_translate") {
        const ytMatch = text.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
        const videoId = ytMatch ? ytMatch[1] : null;

        if (!videoId) {
          addBot("❌ Could not extract YouTube video ID. Please paste a valid YouTube link.");
        } else {
          // Ask user which language to translate to
          const update = addBot("");
          update({
            content: `🎬 **YouTube Video Detected!**\n\nI found your YouTube video. Which language would you like the audio translated to?\n\nReply with the language name like:\n- **Hindi**\n- **Telugu**  \n- **Tamil**\n- **English**\n- **Spanish**\n- Any other language`,
            youtubeVideoId: videoId,
            awaitingLanguage: true
          });
          setCurrentYoutubeId(videoId);
        }
        setLoading(false);
        return;
      }

            // ── IMAGE ──────────────────────────────────────────
      if (detectedMode === "image") {
        fd.append("prompt", text);
        const update = addBot("🎨 Generating your image... (10-20 seconds)");
        const res = await axios.post(`${API}/api/generate-image`, fd);
        if (res.data.image) {
          update({ content: `✅ Here is your generated image for: **${text}**`, image: res.data.image });
        } else {
          update({ content: `❌ Image generation failed: ${res.data.error || "Unknown error"}` });
        }
      }

      // ── WEB SEARCH ────────────────────────────────────
      else if (detectedMode === "search") {
        fd.append("query", text);
        fd.append("language", language);
        const update = addBot("🔍 Searching the live internet...");
        const res = await axios.post(`${API}/api/web-search`, fd);
        update({ content: res.data.answer || `❌ Search failed: ${res.data.error}` });
      }

      // ── CODE ──────────────────────────────────────────
      else if (detectedMode === "code") {
        fd.append("query", text);
        fd.append("language", language);
        const update = addBot("");
        let full = "";
        await streamResponse(`${API}/api/code`, fd,
          delta => { full += delta; update({ content: full }); },
          done => {
            if (done.execution) {
              update({ content: full, execution_output: done.output, execution_success: done.success });
            }
          }
        );
      }

      // ── MATH ──────────────────────────────────────────
      else if (detectedMode === "math") {
        fd.append("problem", text);
        fd.append("language", language);
        const update = addBot("");
        let full = "";
        await streamResponse(`${API}/api/math`, fd,
          delta => { full += delta; update({ content: full }); },
          () => {}
        );
      }

      // ── RESEARCH ──────────────────────────────────────
      else if (detectedMode === "research") {
        fd.append("topic", text);
        fd.append("language", language);
        const update = addBot("📊 Generating comprehensive research report...");
        let full = "";
        await streamResponse(`${API}/api/research`, fd,
          delta => { full += delta; update({ content: full }); },
          () => {}
        );
      }

      // ── PDF CHAT ──────────────────────────────────────
      else if (detectedMode === "pdf" && pdfUploaded) {
        fd.append("message", text);
        fd.append("language", language);
        const update = addBot("");
        let full = "";
        await streamResponse(`${API}/api/pdf-chat`, fd,
          delta => { full += delta; update({ content: full }); },
          () => {}
        );
      }

      // ── EMAIL / SQL / DEBATE / TUTOR via chat API ─────
      else if (["email", "sql", "debate", "tutor", "resume"].includes(detectedMode)) {
        const modePrompts = {
          email: `Write a professional email for this situation: ${text}`,
          sql: `Convert this to SQL with explanation: ${text}`,
          debate: `Debate both sides of this topic thoroughly: ${text}`,
          tutor: `Teach me about this step by step with examples and a quiz: ${text}`,
          resume: `Analyze this resume and provide detailed feedback: ${text}`
        };
        fd.append("message", modePrompts[detectedMode] || text);
        fd.append("language", language);
        if (currentSession) fd.append("session_id", currentSession);
        const update = addBot("");
        let full = "", src = "", conf = null;
        await streamResponse(`${API}/api/chat`, fd,
          delta => { full += delta; update({ content: full }); },
          done => {
            src = done.source || "";
            conf = done.confidence;
            update({ content: full, source: src, confidence: conf });
          }
        );
        loadSessions();
      }

      // ── DEFAULT CHAT ──────────────────────────────────
      else {
        fd.append("message", text);
        fd.append("language", language);
        if (currentSession) fd.append("session_id", currentSession);
        const update = addBot("");
        let full = "", src = "", conf = null;
        await streamResponse(`${API}/api/chat`, fd,
          delta => { full += delta; update({ content: full }); },
          done => {
            src = done.source || "";
            conf = done.confidence;
            update({ content: full, source: src, confidence: conf });
          }
        );
        loadSessions();
      }

    } catch (e) {
      addBot(`❌ **Error:** ${e.message}\n\nMake sure the Flask API is running:\n\`\`\`bash\npython flask_api.py\n\`\`\``);
    }

    setLoading(false);
  };

  return (
    <div style={{
      display: "flex", height: "100vh",
      background: theme.bg, color: theme.text,
      fontFamily: "Inter, sans-serif",
      transition: "all 0.3s"
    }}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 4px; }
        textarea:focus, input:focus, select:focus { outline: none; }
        @keyframes msgIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
        @keyframes typingDot { 0%,100%{opacity:.3;transform:scale(.8)} 50%{opacity:1;transform:scale(1.2)} }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
      `}</style>

      {/* Sidebar */}
      <Sidebar
        theme={theme} isDark={isDark} setIsDark={setIsDark}
        mode={mode} setMode={setMode}
        sessions={sessions} currentSession={currentSession}
        onNewChat={newChat} onLoadSession={loadSession}
        onDeleteSession={deleteSession}
        language={language} setLanguage={setLanguage}
        sidebarOpen={sidebarOpen}
      />

      {/* Main Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>

        {/* Header */}
        <div style={{
          padding: "12px 20px",
          borderBottom: `1px solid ${theme.border}`,
          background: theme.bg2,
          display: "flex", alignItems: "center", gap: "12px"
        }}>
          {/* Sidebar toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{
              background: "none", border: "none",
              color: theme.text2, cursor: "pointer", fontSize: "20px"
            }}
          >☰</button>

          {/* Logo */}
          <span style={{
            fontWeight: "800", fontSize: "16px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>PVBotX</span>

          {/* Current mode indicator */}
          {mode !== "chat" && (
            <div style={{
              display: "flex", alignItems: "center", gap: "6px",
              padding: "4px 12px",
              background: `${FEATURES.find(f => f.id === mode)?.color || "#6366f1"}20`,
              border: `1px solid ${FEATURES.find(f => f.id === mode)?.color || "#6366f1"}40`,
              borderRadius: "20px",
              fontSize: "12px",
              color: FEATURES.find(f => f.id === mode)?.color || "#6366f1"
            }}>
              <span>{FEATURES.find(f => f.id === mode)?.icon}</span>
              <span>{FEATURES.find(f => f.id === mode)?.label} Mode</span>
              <button
                onClick={() => setMode("chat")}
                style={{
                  background: "none", border: "none",
                  color: "inherit", cursor: "pointer",
                  fontSize: "14px", marginLeft: "4px", opacity: 0.7
                }}
              >×</button>
            </div>
          )}

          {mode === "chat" && (
            <div style={{
              fontSize: "11px", color: theme.text2,
              background: "rgba(99,102,241,0.08)",
              border: "1px solid rgba(99,102,241,0.15)",
              padding: "3px 10px", borderRadius: "20px"
            }}>✨ Auto-detect mode</div>
          )}

          {/* PDF indicator */}
          {pdfUploaded && (
            <span style={{
              background: "rgba(16,185,129,0.1)",
              border: "1px solid rgba(16,185,129,0.3)",
              color: "#10b981", padding: "3px 10px",
              borderRadius: "20px", fontSize: "11px"
            }}>📄 {pdfName}</span>
          )}

          {/* Right controls */}
          <div style={{ marginLeft: "auto", display: "flex", gap: "8px", alignItems: "center" }}>
            
            <a href="/" style={{ textDecoration: "none" }}>
              <button style={{
                padding: "6px 14px", background: "none",
                border: `1px solid ${theme.border}`,
                borderRadius: "8px", color: theme.text2,
                cursor: "pointer", fontSize: "12px"
              }}>← Home</button>
            </a>
          </div>
        </div>

        {/* Messages Area */}
        <div style={{ flex: 1, overflow: "auto", padding: "24px 20px" }}>
          {messages.length === 0
            ? <WelcomeScreen
                theme={theme}
                isDark={isDark}
                onExample={text => { setInput(text); textareaRef.current?.focus(); }}
              />
            : messages.map((msg, i) => <Message key={i} msg={msg} theme={theme} onOpenPlayer={(videoId, translation, lang) => {
              setCurrentYoutubeId(videoId);
              setYoutubeTranslation(translation);
              setTargetLang(lang);
              setShowYoutubePlayer(true);
            }} />)
          }

          {loading && (
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <div style={{
                width: "34px", height: "34px", borderRadius: "50%",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: "16px", flexShrink: 0
              }}>🤖</div>
              <TypingDots theme={theme} />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div style={{
          padding: "12px 20px 16px",
          borderTop: `1px solid ${theme.border}`,
          background: theme.bg2
        }}>
          <div style={{
            display: "flex", gap: "8px", alignItems: "flex-end",
            background: theme.input,
            border: `1px solid ${theme.border}`,
            borderRadius: "16px",
            padding: "8px 8px 8px 16px",
            maxWidth: "800px", margin: "0 auto",
            transition: "border-color 0.2s"
          }}
            onFocus={() => {}}
          >
            {/* PDF Upload button */}
            <>
              <input
                ref={fileInputRef}
                type="file" accept=".pdf"
                style={{ display: "none" }}
                onChange={e => e.target.files[0] && uploadPDF(e.target.files[0])}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                title="Upload PDF"
                style={{
                  width: "34px", height: "34px", borderRadius: "8px",
                  background: pdfUploaded ? "rgba(16,185,129,0.15)" : theme.hover,
                  border: `1px solid ${pdfUploaded ? "rgba(16,185,129,0.3)" : theme.border}`,
                  color: pdfUploaded ? "#10b981" : theme.text2,
                  cursor: "pointer", fontSize: "15px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0, transition: "all 0.2s"
                }}
              >📎</button>
            </>

            {/* Text input */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => {
                setInput(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
              }}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask me anything — I'll automatically detect if you want search, images, code, math..."
              rows={1}
              style={{
                flex: 1, background: "transparent",
                border: "none", outline: "none",
                color: theme.text, fontSize: "14px",
                resize: "none", lineHeight: "1.5",
                fontFamily: "Inter, sans-serif",
                maxHeight: "120px", minHeight: "24px"
              }}
            />

            {/* Send button */}
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              style={{
                width: "36px", height: "36px", borderRadius: "10px",
                background: loading || !input.trim()
                  ? theme.hover
                  : "linear-gradient(135deg, #6366f1, #06b6d4)",
                border: "none", color: "white",
                cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                fontSize: "16px",
                display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.2s", flexShrink: 0,
                opacity: loading || !input.trim() ? 0.4 : 1
              }}
            >{loading ? "⏳" : "↑"}</button>

            {/* Voice Input — Right Edge like Claude/GPT */}
            <button
              onClick={isRecording ? stopVoiceInput : startVoiceInput}
              title={isRecording ? "Stop recording" : "Voice input"}
              style={{
                width: "36px", height: "36px", borderRadius: "10px",
                background: isRecording
                  ? "rgba(239,68,68,0.2)"
                  : theme.hover,
                border: `1px solid ${isRecording ? "rgba(239,68,68,0.5)" : theme.border}`,
                color: isRecording ? "#ef4444" : theme.text2,
                cursor: "pointer", fontSize: "16px",
                display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.2s", flexShrink: 0,
                animation: isRecording ? "pulse 1s ease infinite" : "none"
              }}
            >
              {isRecording ? "🔴" : "🎙️"}
            </button>
          </div>

          {/* Hint text */}
          <div style={{
            textAlign: "center", fontSize: "11px",
            color: theme.text2, marginTop: "6px", opacity: 0.5
          }}>
            Enter to send • Shift+Enter for new line • 📎 to upload PDF
          </div>
        </div>
          {/* YouTube Translator Player Modal */}
      {showYoutubePlayer && currentYoutubeId && (
        <YouTubePlayer
          videoId={currentYoutubeId}
          translation={youtubeTranslation}
          targetLang={targetLang}
          theme={theme}
          onClose={() => {
            setShowYoutubePlayer(false);
            window.speechSynthesis.cancel();
          }}
        />
      )}
      </div>
    </div>
  );
  console.log({
  currentYoutubeId,
  youtubeTranslation,
  targetLang
});
}
