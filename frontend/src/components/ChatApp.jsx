import { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import "../index.css";

const API = "http://localhost:8000";

const MODES = [
  { id: "chat", icon: "💬", label: "Chat", desc: "Ask anything" },
  { id: "search", icon: "🔍", label: "Web Search", desc: "Live internet" },
  { id: "image", icon: "🖼️", label: "Image Gen", desc: "Create images" },
  { id: "math", icon: "🧮", label: "Math Solver", desc: "Step by step" },
  { id: "code", icon: "💻", label: "Code", desc: "Write & run code" },
  { id: "pdf", icon: "📄", label: "PDF Chat", desc: "Chat with docs" },
];

const LANGUAGES = [
  "English", "Hindi", "Spanish", "French", "German",
  "Arabic", "Chinese", "Japanese", "Portuguese", "Telugu", "Tamil"
];

function TypingIndicator() {
  return (
    <div style={{
      display: "flex", gap: "4px", padding: "12px 16px",
      background: "rgba(255,255,255,0.03)",
      borderRadius: "16px", width: "fit-content",
      border: "1px solid rgba(255,255,255,0.06)"
    }}>
      {[0,1,2].map(i => (
        <div key={i} style={{
          width: "6px", height: "6px",
          borderRadius: "50%",
          background: "rgba(99,102,241,0.8)",
          animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`
        }}/>
      ))}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1.2); }
        }
      `}</style>
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";

  return (
    <div style={{
      display: "flex",
      justifyContent: isUser ? "flex-end" : "flex-start",
      marginBottom: "16px",
      animation: "fadeIn 0.3s ease"
    }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {!isUser && (
        <div style={{
          width: "32px", height: "32px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          display: "flex", alignItems: "center",
          justifyContent: "center",
          fontSize: "14px", marginRight: "10px",
          flexShrink: 0, marginTop: "4px"
        }}>🤖</div>
      )}

      <div style={{
        maxWidth: "75%",
        padding: "12px 16px",
        borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
        background: isUser
          ? "linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2))"
          : "rgba(255,255,255,0.04)",
        border: `1px solid ${isUser ? "rgba(99,102,241,0.3)" : "rgba(255,255,255,0.06)"}`,
        fontSize: "14px",
        lineHeight: "1.6",
        color: "#f0f0ff"
      }}>
        {msg.image && (
          <img
            src={`data:image/jpeg;base64,${msg.image}`}
            style={{ width: "100%", borderRadius: "8px", marginBottom: "8px" }}
            alt="generated"
          />
        )}
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{ borderRadius: "8px", margin: "8px 0", fontSize: "13px" }}
                  {...props}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              ) : (
                <code style={{
                  background: "rgba(99,102,241,0.2)",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  fontSize: "13px"
                }} {...props}>{children}</code>
              );
            }
          }}
        >
          {msg.content}
        </ReactMarkdown>

        {msg.execution_output && (
          <div style={{
            marginTop: "8px",
            padding: "10px",
            background: msg.execution_success ? "#0d1117" : "#1a0505",
            borderRadius: "8px",
            fontFamily: "monospace",
            fontSize: "12px",
            color: msg.execution_success ? "#00ff88" : "#ff6b6b",
            border: `1px solid ${msg.execution_success ? "#00ff8830" : "#ff6b6b30"}`
          }}>
            {msg.execution_success ? "▶ Output:" : "❌ Error:"} {msg.execution_output}
          </div>
        )}

        {msg.source && (
          <div style={{
            marginTop: "8px",
            fontSize: "11px",
            color: "rgba(99,102,241,0.8)",
            borderTop: "1px solid rgba(255,255,255,0.06)",
            paddingTop: "6px"
          }}>
            📚 {msg.source}
            {msg.confidence && (
              <span style={{
                marginLeft: "8px",
                background: msg.confidence >= 80 ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.2)",
                color: msg.confidence >= 80 ? "#10b981" : "#f59e0b",
                padding: "1px 6px",
                borderRadius: "10px",
                fontSize: "10px"
              }}>
                {msg.confidence}% confident
              </span>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div style={{
          width: "32px", height: "32px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          display: "flex", alignItems: "center",
          justifyContent: "center",
          fontSize: "14px", marginLeft: "10px",
          flexShrink: 0, marginTop: "4px"
        }}>🧑</div>
      )}
    </div>
  );
}

function Sidebar({ mode, setMode, sessions, currentSession, onNewChat, onLoadSession, onDeleteSession, language, setLanguage }) {
  return (
    <div style={{
      width: "260px",
      background: "rgba(255,255,255,0.02)",
      borderRight: "1px solid rgba(255,255,255,0.06)",
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      flexShrink: 0
    }}>
      {/* Logo */}
      <div style={{
        padding: "20px 16px 16px",
        borderBottom: "1px solid rgba(255,255,255,0.06)"
      }}>
        <div style={{
          display: "flex", alignItems: "center", gap: "10px",
          marginBottom: "16px"
        }}>
          <div style={{
            width: "36px", height: "36px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: "18px"
          }}>🤖</div>
          <div>
            <div style={{ fontWeight: "600", fontSize: "15px" }}>Aurora AI</div>
            <div style={{ fontSize: "11px", color: "rgba(99,102,241,0.8)" }}>Powered by Llama 3</div>
          </div>
        </div>

        <button
          onClick={onNewChat}
          style={{
            width: "100%",
            padding: "8px 12px",
            background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.1))",
            border: "1px solid rgba(99,102,241,0.3)",
            borderRadius: "8px",
            color: "#f0f0ff",
            cursor: "pointer",
            fontSize: "13px",
            fontWeight: "500",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            justifyContent: "center"
          }}
        >
          ✏️ New Chat
        </button>
      </div>

      {/* Modes */}
      <div style={{ padding: "12px 10px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.3)", padding: "0 6px 8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Modes
        </div>
        {MODES.map(m => (
          <button
            key={m.id}
            onClick={() => setMode(m.id)}
            style={{
              width: "100%",
              padding: "8px 10px",
              background: mode === m.id
                ? "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.1))"
                : "transparent",
              border: mode === m.id
                ? "1px solid rgba(99,102,241,0.3)"
                : "1px solid transparent",
              borderRadius: "8px",
              color: mode === m.id ? "#f0f0ff" : "rgba(255,255,255,0.5)",
              cursor: "pointer",
              fontSize: "13px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "2px",
              textAlign: "left",
              transition: "all 0.2s"
            }}
          >
            <span style={{ fontSize: "16px" }}>{m.icon}</span>
            <div>
              <div style={{ fontWeight: mode === m.id ? "500" : "400" }}>{m.label}</div>
              <div style={{ fontSize: "10px", opacity: 0.5 }}>{m.desc}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Language */}
      <div style={{ padding: "12px 16px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.3)", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Language
        </div>
        <select
          value={language}
          onChange={e => setLanguage(e.target.value)}
          style={{
            width: "100%",
            padding: "6px 10px",
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "6px",
            color: "#f0f0ff",
            fontSize: "13px",
            cursor: "pointer"
          }}
        >
          {LANGUAGES.map(l => <option key={l} value={l} style={{ background: "#1a1a2e" }}>{l}</option>)}
        </select>
      </div>

      {/* Chat History */}
      <div style={{ flex: 1, overflow: "auto", padding: "12px 10px" }}>
        <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.3)", padding: "0 6px 8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Recent Chats
        </div>
        {sessions.slice(0, 8).map(s => (
          <div
            key={s.id}
            style={{
              display: "flex",
              alignItems: "center",
              padding: "6px 8px",
              borderRadius: "6px",
              cursor: "pointer",
              marginBottom: "2px",
              background: currentSession === s.id ? "rgba(99,102,241,0.1)" : "transparent",
              border: currentSession === s.id ? "1px solid rgba(99,102,241,0.2)" : "1px solid transparent"
            }}
          >
            <span
              style={{ flex: 1, fontSize: "12px", color: "rgba(255,255,255,0.6)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
              onClick={() => onLoadSession(s.id)}
            >
              💬 {s.name}
            </span>
            <button
              onClick={() => onDeleteSession(s.id)}
              style={{ background: "none", border: "none", color: "rgba(255,255,255,0.2)", cursor: "pointer", fontSize: "12px", padding: "0 2px" }}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("chat");
  const [language, setLanguage] = useState("English");
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [pdfName, setPdfName] = useState("");
  const [imagePrompt, setImagePrompt] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
  }, []);

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
      const res = await axios.post(`${API}/api/sessions`, new URLSearchParams({ name: "New Chat" }));
      setCurrentSession(res.data.id);
      setMessages([]);
      await axios.post(`${API}/api/clear-history`);
      loadSessions();
    } catch (e) {
      setMessages([]);
      setCurrentSession(null);
    }
  };

  const loadSession = async (id) => {
    try {
      const res = await axios.get(`${API}/api/sessions/${id}/messages`);
      const msgs = res.data.map(m => ({ role: m.role, content: m.content }));
      setMessages(msgs);
      setCurrentSession(id);
    } catch (e) {}
  };

  const deleteSession = async (id) => {
    try {
      await axios.delete(`${API}/api/sessions/${id}`);
      if (currentSession === id) {
        setMessages([]);
        setCurrentSession(null);
      }
      loadSessions();
    } catch (e) {}
  };

  const sendMessage = async (text = input) => {
    if (!text.trim() || loading) return;
    setInput("");
    setLoading(true);

    const userMsg = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);

    try {
      if (mode === "search") {
        const formData = new FormData();
        formData.append("query", text);
        formData.append("language", language);
        const res = await axios.post(`${API}/api/web-search`, formData);
        setMessages(prev => [...prev, { role: "assistant", content: res.data.answer }]);

      } else if (mode === "image") {
        const formData = new FormData();
        formData.append("prompt", text);
        const res = await axios.post(`${API}/api/generate-image`, formData);
        if (res.data.image) {
          setMessages(prev => [...prev, {
            role: "assistant",
            content: `Here is your generated image for: **${text}**`,
            image: res.data.image
          }]);
        }

      } else if (mode === "math") {
        const formData = new FormData();
        formData.append("problem", text);
        formData.append("language", language);

        const response = await fetch(`${API}/api/math`, { method: "POST", body: formData });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = "";

        setMessages(prev => [...prev, { role: "assistant", content: "" }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
          for (const line of lines) {
            const data = JSON.parse(line.slice(6));
            if (data.type === "delta") {
              fullContent += data.content;
              setMessages(prev => {
                const msgs = [...prev];
                msgs[msgs.length - 1] = { role: "assistant", content: fullContent };
                return msgs;
              });
            }
          }
        }

      } else if (mode === "code") {
        const formData = new FormData();
        formData.append("query", text);
        formData.append("language", language);

        const response = await fetch(`${API}/api/code`, { method: "POST", body: formData });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = "";
        let execOutput = null;
        let execSuccess = false;

        setMessages(prev => [...prev, { role: "assistant", content: "" }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
          for (const line of lines) {
            const data = JSON.parse(line.slice(6));
            if (data.type === "delta") {
              fullContent += data.content;
              setMessages(prev => {
                const msgs = [...prev];
                msgs[msgs.length - 1] = { role: "assistant", content: fullContent };
                return msgs;
              });
            } else if (data.type === "execution") {
              execOutput = data.output;
              execSuccess = data.success;
              setMessages(prev => {
                const msgs = [...prev];
                msgs[msgs.length - 1] = {
                  role: "assistant",
                  content: fullContent,
                  execution_output: execOutput,
                  execution_success: execSuccess
                };
                return msgs;
              });
            }
          }
        }

      } else if (mode === "pdf") {
        if (!pdfUploaded) {
          setMessages(prev => [...prev, { role: "assistant", content: "Please upload a PDF first using the 📎 button below." }]);
        } else {
          const formData = new FormData();
          formData.append("message", text);
          formData.append("language", language);

          const response = await fetch(`${API}/api/pdf-chat`, { method: "POST", body: formData });
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let fullContent = "";

          setMessages(prev => [...prev, { role: "assistant", content: "" }]);

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
            for (const line of lines) {
              const data = JSON.parse(line.slice(6));
              if (data.type === "delta") {
                fullContent += data.content;
                setMessages(prev => {
                  const msgs = [...prev];
                  msgs[msgs.length - 1] = { role: "assistant", content: fullContent };
                  return msgs;
                });
              }
            }
          }
        }

      } else {
        const formData = new FormData();
        formData.append("message", text);
        formData.append("language", language);
        if (currentSession) formData.append("session_id", currentSession);

        const response = await fetch(`${API}/api/chat`, { method: "POST", body: formData });
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = "";
        let source = "";
        let confidence = null;

        setMessages(prev => [...prev, { role: "assistant", content: "" }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
          for (const line of lines) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "delta") {
                fullContent += data.content;
                setMessages(prev => {
                  const msgs = [...prev];
                  msgs[msgs.length - 1] = { role: "assistant", content: fullContent, source, confidence };
                  return msgs;
                });
              } else if (data.type === "done") {
                source = data.source;
                confidence = data.confidence;
                setMessages(prev => {
                  const msgs = [...prev];
                  msgs[msgs.length - 1] = { role: "assistant", content: fullContent, source, confidence };
                  return msgs;
                });
              }
            } catch (e) {}
          }
        }
        loadSessions();
      }

    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${e.message}. Make sure the API server is running.` }]);
    }

    setLoading(false);
  };

  const uploadPDF = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API}/api/upload-pdf`, formData);
      if (res.data.success) {
        setPdfUploaded(true);
        setPdfName(res.data.filename);
        setMessages(prev => [...prev, {
          role: "assistant",
          content: `✅ **${res.data.filename}** loaded successfully! (${res.data.chunks} chunks)\n\nYou can now ask me anything about this PDF.`
        }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "Failed to upload PDF. Make sure the API server is running." }]);
    }
  };

  const getModeInfo = () => {
    const m = MODES.find(m => m.id === mode);
    return m || MODES[0];
  };

  return (
    <div className="app">
      <div className="aurora-bg" />

      <Sidebar
        mode={mode}
        setMode={(m) => { setMode(m); setMessages([]); }}
        sessions={sessions}
        currentSession={currentSession}
        onNewChat={newChat}
        onLoadSession={loadSession}
        onDeleteSession={deleteSession}
        language={language}
        setLanguage={setLanguage}
      />

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>

        {/* Header */}
        <div style={{
          padding: "14px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(255,255,255,0.01)",
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <span style={{ fontSize: "20px" }}>{getModeInfo().icon}</span>
          <div>
            <div style={{ fontWeight: "600", fontSize: "15px" }}>{getModeInfo().label}</div>
            <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)" }}>{getModeInfo().desc}</div>
          </div>
          {pdfUploaded && mode === "pdf" && (
            <span style={{
              marginLeft: "auto",
              background: "rgba(16,185,129,0.15)",
              border: "1px solid rgba(16,185,129,0.3)",
              color: "#10b981",
              padding: "3px 10px",
              borderRadius: "20px",
              fontSize: "11px"
            }}>
              📄 {pdfName}
            </span>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflow: "auto", padding: "24px" }}>
          {messages.length === 0 && (
            <div style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              gap: "12px",
              opacity: 0.6
            }}>
              <div style={{ fontSize: "48px" }}>{getModeInfo().icon}</div>
              <div style={{ fontSize: "20px", fontWeight: "600" }}>
                {getModeInfo().label} Mode
              </div>
              <div style={{ fontSize: "13px", color: "rgba(255,255,255,0.4)", textAlign: "center" }}>
                {mode === "chat" && "Ask me anything — I search Wikipedia and answer intelligently"}
                {mode === "search" && "Search the live internet like Perplexity AI"}
                {mode === "image" && "Describe any image and I will generate it for you"}
                {mode === "math" && "Enter any math problem for step by step solution"}
                {mode === "code" && "Ask coding questions — I write and execute code"}
                {mode === "pdf" && "Upload a PDF and ask questions about it"}
              </div>
            </div>
          )}

          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && (
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <div style={{
                width: "32px", height: "32px", borderRadius: "50%",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "14px", flexShrink: 0
              }}>🤖</div>
              <TypingIndicator />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: "16px 24px",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(255,255,255,0.01)"
        }}>
          <div style={{
            display: "flex",
            gap: "10px",
            alignItems: "flex-end",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: "16px",
            padding: "8px 8px 8px 16px",
            transition: "border-color 0.2s"
          }}>
            {mode === "pdf" && (
              <label style={{ cursor: "pointer", flexShrink: 0 }}>
                <input
                  type="file"
                  accept=".pdf"
                  style={{ display: "none" }}
                  onChange={e => e.target.files[0] && uploadPDF(e.target.files[0])}
                />
                <span style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "36px",
                  height: "36px",
                  borderRadius: "8px",
                  background: "rgba(99,102,241,0.15)",
                  fontSize: "18px",
                  cursor: "pointer"
                }}>📎</span>
              </label>
            )}

            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={
                mode === "chat" ? "Ask anything... (Enter to send, Shift+Enter for new line)" :
                mode === "search" ? "Search the internet..." :
                mode === "image" ? "Describe the image you want to generate..." :
                mode === "math" ? "Enter your math problem..." :
                mode === "code" ? "Ask a coding question..." :
                "Ask about the PDF..."
              }
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                outline: "none",
                color: "#f0f0ff",
                fontSize: "14px",
                resize: "none",
                minHeight: "24px",
                maxHeight: "120px",
                lineHeight: "1.5",
                fontFamily: "Inter, sans-serif"
              }}
              rows={1}
            />

            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: loading || !input.trim()
                  ? "rgba(255,255,255,0.05)"
                  : "linear-gradient(135deg, #6366f1, #06b6d4)",
                border: "none",
                color: "#fff",
                cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "16px",
                flexShrink: 0,
                transition: "all 0.2s"
              }}
            >
              {loading ? "⏳" : "↑"}
            </button>
          </div>

          <div style={{
            textAlign: "center",
            fontSize: "11px",
            color: "rgba(255,255,255,0.2)",
            marginTop: "8px"
          }}>
            Aurora AI • Powered by Llama 3.3 + Wikipedia + FAISS
          </div>
        </div>
      </div>
    </div>
  );
}