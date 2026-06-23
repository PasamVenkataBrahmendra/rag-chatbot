import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import axios from "axios";

const API = "http://localhost:8000";

// ── THEME ──────────────────────────────────────────────────
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

// ── TYPING INDICATOR ───────────────────────────────────────
function TypingDots({ theme }) {
  return (
    <div style={{ display: "flex", gap: "5px", padding: "14px 18px", background: theme.botBubble, borderRadius: "18px 18px 18px 4px", border: `1px solid ${theme.border}`, width: "fit-content" }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: "7px", height: "7px", borderRadius: "50%",
          background: "#6366f1",
          animation: `typingDot 1.2s ease-in-out ${i * 0.2}s infinite`
        }} />
      ))}
      <style>{`
        @keyframes typingDot {
          0%,100% { opacity:0.3; transform:scale(0.8); }
          50% { opacity:1; transform:scale(1.2); }
        }
        @keyframes msgIn {
          from { opacity:0; transform:translateY(10px); }
          to { opacity:1; transform:translateY(0); }
        }
      `}</style>
    </div>
  );
}

// ── MESSAGE ────────────────────────────────────────────────
function Message({ msg, theme }) {
  const isUser = msg.role === "user";

  return (
    <div style={{
      display: "flex",
      justifyContent: isUser ? "flex-end" : "flex-start",
      marginBottom: "16px",
      animation: "msgIn 0.3s ease"
    }}>
      {!isUser && (
        <div style={{
          width: "34px", height: "34px", borderRadius: "50%",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "16px", marginRight: "10px", flexShrink: 0, marginTop: "2px"
        }}>🤖</div>
      )}

      <div style={{ maxWidth: "78%" }}>
        <div style={{
          padding: "13px 18px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser
            ? `linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2))`
            : theme.botBubble,
          border: `1px solid ${isUser ? "rgba(99,102,241,0.3)" : theme.border}`,
          color: theme.text,
          fontSize: "14px",
          lineHeight: "1.65"
        }}>
          {msg.image && (
            <img src={`data:image/jpeg;base64,${msg.image}`}
              style={{ width: "100%", borderRadius: "10px", marginBottom: "10px" }}
              alt="generated" />
          )}

          <ReactMarkdown components={{
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
          }}>{msg.content}</ReactMarkdown>

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

        {msg.source && (
          <div style={{ marginTop: "5px", fontSize: "11px", color: theme.text2, paddingLeft: "4px", display: "flex", gap: "8px", alignItems: "center" }}>
            <span>📚 {msg.source}</span>
            {msg.confidence && (
              <span style={{
                background: msg.confidence >= 80 ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)",
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
          fontSize: "16px", marginLeft: "10px", flexShrink: 0, marginTop: "2px"
        }}>🧑</div>
      )}
    </div>
  );
}

// ── SIDEBAR ────────────────────────────────────────────────
function Sidebar({ theme, isDark, setIsDark, mode, setMode, sessions, currentSession, onNewChat, onLoadSession, onDeleteSession, language, setLanguage, sidebarOpen }) {
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
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
          <div style={{
            width: "36px", height: "36px", borderRadius: "10px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px"
          }}>🤖</div>
          <span style={{
            fontWeight: "800", fontSize: "18px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>PVBotX</span>
          <button
            onClick={() => setIsDark(!isDark)}
            style={{
              marginLeft: "auto", background: "none", border: "none",
              fontSize: "18px", cursor: "pointer"
            }}
          >{isDark ? "☀️" : "🌙"}</button>
        </div>
        <button
          onClick={onNewChat}
          style={{
            width: "100%", padding: "8px",
            background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1))",
            border: `1px solid rgba(99,102,241,0.3)`,
            borderRadius: "8px", color: theme.text,
            cursor: "pointer", fontSize: "13px", fontWeight: "500"
          }}
        >✏️ New Chat</button>
      </div>

      {/* Language */}
      <div style={{ padding: "10px 14px", borderBottom: `1px solid ${theme.border}` }}>
        <div style={{ fontSize: "10px", color: theme.text2, marginBottom: "5px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Language</div>
        <select
          value={language}
          onChange={e => setLanguage(e.target.value)}
          style={{
            width: "100%", padding: "5px 8px",
            background: theme.input, border: `1px solid ${theme.border}`,
            borderRadius: "6px", color: theme.text, fontSize: "12px", cursor: "pointer"
          }}
        >
          {LANGUAGES.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
      </div>

      {/* Modes */}
      <div style={{ padding: "10px 10px", borderBottom: `1px solid ${theme.border}`, overflow: "auto", maxHeight: "300px" }}>
        <div style={{ fontSize: "10px", color: theme.text2, padding: "0 4px 6px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Features</div>
        {FEATURES.map(f => (
          <button
            key={f.id}
            onClick={() => setMode(f.id)}
            style={{
              width: "100%", padding: "7px 10px",
              background: mode === f.id ? `${f.color}22` : "transparent",
              border: `1px solid ${mode === f.id ? f.color + "44" : "transparent"}`,
              borderRadius: "7px", color: mode === f.id ? f.color : theme.text2,
              cursor: "pointer", fontSize: "12px",
              display: "flex", alignItems: "center", gap: "8px",
              marginBottom: "2px", textAlign: "left", transition: "all 0.15s"
            }}
          >
            <span>{f.icon}</span>
            <span style={{ fontWeight: mode === f.id ? "600" : "400" }}>{f.label}</span>
            <span style={{ marginLeft: "auto", fontSize: "10px", opacity: 0.4 }}>{f.desc}</span>
          </button>
        ))}
      </div>

      {/* Chat History */}
      <div style={{ flex: 1, overflow: "auto", padding: "10px" }}>
        <div style={{ fontSize: "10px", color: theme.text2, padding: "0 4px 6px", textTransform: "uppercase", letterSpacing: "0.5px" }}>History</div>
        {sessions.slice(0, 10).map(s => (
          <div key={s.id} style={{ display: "flex", alignItems: "center", marginBottom: "2px" }}>
            <button
              onClick={() => onLoadSession(s.id)}
              style={{
                flex: 1, padding: "6px 8px", background: currentSession === s.id ? theme.hover : "transparent",
                border: "none", borderRadius: "6px", color: theme.text2,
                cursor: "pointer", fontSize: "11px", textAlign: "left",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap"
              }}
            >💬 {s.name}</button>
            <button
              onClick={() => onDeleteSession(s.id)}
              style={{ background: "none", border: "none", color: theme.text2, cursor: "pointer", fontSize: "13px", padding: "0 4px", opacity: 0.4 }}
            >×</button>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── FLOATING MENU ──────────────────────────────────────────
function FloatingMenu({ theme, mode, setMode, open, setOpen }) {
  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: "36px", height: "36px", borderRadius: "10px",
          background: open
            ? "linear-gradient(135deg, #6366f1, #06b6d4)"
            : theme.input,
          border: `1px solid ${theme.border}`,
          color: open ? "white" : theme.text,
          cursor: "pointer", fontSize: "18px",
          display: "flex", alignItems: "center", justifyContent: "center",
          transition: "all 0.2s",
          transform: open ? "rotate(45deg)" : "rotate(0deg)"
        }}
      >➕</button>

      {open && (
        <div style={{
          position: "absolute",
          bottom: "48px", left: 0,
          background: theme.bg2,
          border: `1px solid ${theme.border}`,
          borderRadius: "16px",
          padding: "8px",
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "4px",
          width: "260px",
          boxShadow: "0 20px 40px rgba(0,0,0,0.3)",
          zIndex: 100,
          animation: "msgIn 0.2s ease"
        }}>
          {FEATURES.map(f => (
            <button
              key={f.id}
              onClick={() => { setMode(f.id); setOpen(false); }}
              style={{
                padding: "10px 12px",
                background: mode === f.id ? `${f.color}22` : theme.hover,
                border: `1px solid ${mode === f.id ? f.color + "44" : "transparent"}`,
                borderRadius: "10px",
                color: mode === f.id ? f.color : theme.text,
                cursor: "pointer", fontSize: "12px",
                display: "flex", alignItems: "center", gap: "8px",
                transition: "all 0.15s", textAlign: "left"
              }}
            >
              <span style={{ fontSize: "18px" }}>{f.icon}</span>
              <div>
                <div style={{ fontWeight: "500", fontSize: "12px" }}>{f.label}</div>
                <div style={{ fontSize: "10px", opacity: 0.5 }}>{f.desc}</div>
              </div>
            </button>
          ))}
        </div>
      )}
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
  const [menuOpen, setMenuOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const theme = isDark ? THEMES.dark : THEMES.light;
  const currentFeature = FEATURES.find(f => f.id === mode) || FEATURES[0];

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    setMessages([]);
    setMenuOpen(false);
  }, [mode]);

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
        update({ content: `✅ **${res.data.filename}** loaded! (${res.data.chunks} chunks)\n\nAsk me anything about this PDF.` });
      }
    } catch (e) {
      const update = addBot("");
      update({ content: "❌ Failed to upload PDF. Make sure the API is running." });
    }
  };

  const sendMessage = async (text = input) => {
    if (!text.trim() || loading) return;
    setInput("");
    setLoading(true);

    setMessages(prev => [...prev, { role: "user", content: text }]);

    try {
      // ── CHAT ──
      if (mode === "chat") {
        const update = addBot("");
        let full = "", src = "", conf = null;
        const fd = new FormData();
        fd.append("message", text);
        fd.append("language", language);
        if (currentSession) fd.append("session_id", currentSession);

        await streamResponse(`${API}/api/chat`, fd,
          delta => { full += delta; update({ content: full }); },
          done => { src = done.source; conf = done.confidence; update({ content: full, source: src, confidence: conf }); }
        );
        loadSessions();
      }

      // ── WEB SEARCH ──
      else if (mode === "search") {
        const update = addBot("🔍 Searching the web...");
        const fd = new FormData();
        fd.append("query", text);
        fd.append("language", language);
        const res = await axios.post(`${API}/api/web-search`, fd);
        update({ content: res.data.answer || res.data.error });
      }

      // ── IMAGE ──
      else if (mode === "image") {
        const update = addBot("🎨 Generating your image...");
        const fd = new FormData();
        fd.append("prompt", text);
        const res = await axios.post(`${API}/api/generate-image`, fd);
        if (res.data.image) {
          update({ content: `Here is your generated image for: **${text}**`, image: res.data.image });
        } else {
          update({ content: `❌ Failed: ${res.data.error}` });
        }
      }

      // ── PDF CHAT ──
      else if (mode === "pdf") {
        if (!pdfUploaded) {
          addBot("Please upload a PDF first using the 📎 button.");
        } else {
          const update = addBot("");
          let full = "";
          const fd = new FormData();
          fd.append("message", text);
          fd.append("language", language);
          await streamResponse(`${API}/api/pdf-chat`, fd,
            delta => { full += delta; update({ content: full }); },
            () => {}
          );
        }
      }

      // ── CODE ──
      else if (mode === "code") {
        const update = addBot("");
        let full = "";
        const fd = new FormData();
        fd.append("query", text);
        fd.append("language", language);
        await streamResponse(`${API}/api/code`, fd,
          delta => { full += delta; update({ content: full }); },
          done => {
            if (done.execution) {
              update({ content: full, execution_output: done.output, execution_success: done.success });
            }
          }
        );
      }

      // ── MATH ──
      else if (mode === "math") {
        const update = addBot("");
        let full = "";
        const fd = new FormData();
        fd.append("problem", text);
        fd.append("language", language);
        await streamResponse(`${API}/api/math`, fd,
          delta => { full += delta; update({ content: full }); },
          () => {}
        );
      }

      // ── RESEARCH ──
      else if (mode === "research") {
        const update = addBot("📊 Generating research report...");
        let full = "";
        const fd = new FormData();
        fd.append("topic", text);
        fd.append("language", language);
        await streamResponse(`${API}/api/research`, fd,
          delta => { full += delta; update({ content: full }); },
          () => {}
        );
      }

      // ── ALL OTHER MODES via general chat ──
      else {
        const modePrompts = {
          tutor: `Act as a personal tutor. Teach me about: ${text}`,
          resume: `Analyze this resume content: ${text}`,
          email: `Write a professional email for: ${text}`,
          sql: `Convert to SQL: ${text}`,
          debate: `Debate both sides of: ${text}`
        };
        const update = addBot("");
        let full = "", src = "", conf = null;
        const fd = new FormData();
        fd.append("message", modePrompts[mode] || text);
        fd.append("language", language);
        await streamResponse(`${API}/api/chat`, fd,
          delta => { full += delta; update({ content: full }); },
          done => { src = done.source; conf = done.confidence; update({ content: full, source: src, confidence: conf }); }
        );
      }

    } catch (e) {
      addBot(`❌ Error: ${e.message}. Make sure Flask API is running at port 8000.`);
    }

    setLoading(false);
  };

  const PLACEHOLDERS = {
    chat: "Ask me anything...",
    search: "Search the live internet...",
    image: "Describe the image you want...",
    pdf: pdfUploaded ? `Ask about ${pdfName}...` : "Upload a PDF first, then ask questions...",
    code: "Ask a coding question...",
    math: "Enter your math problem...",
    research: "Enter a research topic...",
    tutor: "What do you want to learn?",
    resume: "Paste resume content to analyze...",
    email: "Describe the email situation...",
    sql: "Describe the query in plain English...",
    debate: "Enter a topic to debate..."
  };

  const WELCOME = {
    chat: { icon: "💬", title: "Chat with PVBotX", sub: "Ask me anything — I search Wikipedia and answer intelligently with source citations" },
    search: { icon: "🔍", title: "Web Search", sub: "Search the live internet like Perplexity AI with real-time Google results" },
    image: { icon: "🖼️", title: "Image Generator", sub: "Describe any image and I will generate it for you using AI" },
    pdf: { icon: "📄", title: "PDF Chat", sub: "Upload a PDF and ask questions with exact page number citations" },
    code: { icon: "💻", title: "Code Interpreter", sub: "Write, explain, debug and actually execute Python code" },
    math: { icon: "🧮", title: "Math Solver", sub: "Enter any math problem for a complete step-by-step solution" },
    research: { icon: "📊", title: "Research Assistant", sub: "Get a full 9-section research report on any topic" },
    tutor: { icon: "🎓", title: "Personal Tutor", sub: "Learn anything step by step with examples, quizzes and follow-ups" },
    resume: { icon: "📋", title: "Resume Analyzer", sub: "Paste your resume content and get detailed professional feedback" },
    email: { icon: "📧", title: "Email Writer", sub: "Describe your situation and get a professional email drafted" },
    sql: { icon: "🗄️", title: "Text to SQL", sub: "Describe what data you want and get the SQL query instantly" },
    debate: { icon: "⚔️", title: "Debate Mode", sub: "Enter any topic and get strong arguments for and against" }
  };

  const welcome = WELCOME[mode] || WELCOME.chat;

  return (
    <div style={{
      display: "flex",
      height: "100vh",
      background: theme.bg,
      color: theme.text,
      fontFamily: "Inter, sans-serif",
      transition: "all 0.3s"
    }}>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 4px; }
        textarea:focus, input:focus, select:focus { outline: none; }
        @keyframes msgIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        @keyframes typingDot { 0%,100%{opacity:.3;transform:scale(.8)} 50%{opacity:1;transform:scale(1.2)} }
      `}</style>

      {/* Sidebar */}
      <Sidebar
        theme={theme} isDark={isDark} setIsDark={setIsDark}
        mode={mode} setMode={setMode}
        sessions={sessions} currentSession={currentSession}
        onNewChat={newChat} onLoadSession={loadSession} onDeleteSession={deleteSession}
        language={language} setLanguage={setLanguage}
        sidebarOpen={sidebarOpen}
      />

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>

        {/* Header */}
        <div style={{
          padding: "12px 20px",
          borderBottom: `1px solid ${theme.border}`,
          background: theme.bg2,
          display: "flex", alignItems: "center", gap: "12px"
        }}>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: "none", border: "none", color: theme.text2, cursor: "pointer", fontSize: "18px" }}
          >☰</button>

          <span style={{ fontSize: "22px" }}>{currentFeature.icon}</span>
          <div>
            <div style={{ fontWeight: "600", fontSize: "14px" }}>{currentFeature.label}</div>
            <div style={{ fontSize: "11px", color: theme.text2 }}>{currentFeature.desc}</div>
          </div>

          {mode === "pdf" && pdfUploaded && (
            <span style={{
              marginLeft: "auto",
              background: "rgba(16,185,129,0.1)",
              border: "1px solid rgba(16,185,129,0.3)",
              color: "#10b981", padding: "3px 10px",
              borderRadius: "20px", fontSize: "11px"
            }}>📄 {pdfName}</span>
          )}

          <div style={{ marginLeft: "auto", display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              onClick={() => setIsDark(!isDark)}
              style={{ background: "none", border: "none", color: theme.text2, cursor: "pointer", fontSize: "18px" }}
            >{isDark ? "☀️" : "🌙"}</button>
            <a href="/" style={{ textDecoration: "none" }}>
              <button style={{
                padding: "6px 14px",
                background: "none",
                border: `1px solid ${theme.border}`,
                borderRadius: "8px", color: theme.text2,
                cursor: "pointer", fontSize: "12px"
              }}>← Home</button>
            </a>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflow: "auto", padding: "24px 20px" }}>
          {messages.length === 0 && (
            <div style={{
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              height: "100%", textAlign: "center", opacity: 0.7
            }}>
              <div style={{ fontSize: "56px", marginBottom: "16px" }}>{welcome.icon}</div>
              <h2 style={{ fontSize: "24px", fontWeight: "700", marginBottom: "8px" }}>{welcome.title}</h2>
              <p style={{ color: theme.text2, fontSize: "14px", maxWidth: "500px", lineHeight: "1.6" }}>{welcome.sub}</p>

              {mode === "pdf" && !pdfUploaded && (
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    marginTop: "24px", padding: "12px 28px",
                    background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                    border: "none", borderRadius: "12px",
                    color: "white", cursor: "pointer", fontSize: "14px", fontWeight: "600"
                  }}
                >📎 Upload PDF to Start</button>
              )}
            </div>
          )}

          {messages.map((msg, i) => <Message key={i} msg={msg} theme={theme} />)}
          {loading && (
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <div style={{
                width: "34px", height: "34px", borderRadius: "50%",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "16px", flexShrink: 0
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
            borderRadius: "16px", padding: "8px 8px 8px 14px",
            transition: "border-color 0.2s",
            maxWidth: "800px", margin: "0 auto"
          }}>
            {/* Floating Menu Button */}
            <FloatingMenu
              theme={theme} mode={mode}
              setMode={m => { setMode(m); setMessages([]); }}
              open={menuOpen} setOpen={setMenuOpen}
            />

            {/* PDF Upload */}
            {mode === "pdf" && (
              <>
                <input
                  ref={fileInputRef}
                  type="file" accept=".pdf"
                  style={{ display: "none" }}
                  onChange={e => e.target.files[0] && uploadPDF(e.target.files[0])}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    width: "36px", height: "36px", borderRadius: "8px",
                    background: pdfUploaded ? "rgba(16,185,129,0.15)" : theme.hover,
                    border: `1px solid ${pdfUploaded ? "rgba(16,185,129,0.3)" : theme.border}`,
                    color: pdfUploaded ? "#10b981" : theme.text2,
                    cursor: "pointer", fontSize: "16px",
                    display: "flex", alignItems: "center", justifyContent: "center"
                  }}
                >📎</button>
              </>
            )}

            {/* Text Input */}
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={PLACEHOLDERS[mode] || "Type your message..."}
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

            {/* Send Button */}
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
                transition: "all 0.2s", flexShrink: 0
              }}
            >{loading ? "⏳" : "↑"}</button>
          </div>

          <div style={{
            textAlign: "center", fontSize: "11px",
            color: theme.text2, marginTop: "6px", opacity: 0.5
          }}>
            PVBotX • Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}