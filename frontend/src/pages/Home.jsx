import { useState } from "react";
import { Link } from "react-router-dom";
import { useInView } from "react-intersection-observer";
import NeuralNetwork from "../components/NeuralNetwork";

const FEATURES = [
  { icon: "🔍", title: "Web Search", desc: "Real-time internet search like Perplexity AI" },
  { icon: "📄", title: "PDF Chat", desc: "Upload documents and chat with page citations" },
  { icon: "🖼️", title: "Image Generation", desc: "Create stunning images from text" },
  { icon: "💻", title: "Code Interpreter", desc: "Write, explain and execute code" },
  { icon: "🧮", title: "Math Solver", desc: "Solve equations step by step" },
  { icon: "🎓", title: "Personal Tutor", desc: "Learn anything with lessons and quizzes" },
  { icon: "📊", title: "Research Assistant", desc: "Full research reports on any topic" },
  { icon: "🎯", title: "Interview Coach", desc: "Practice and get graded feedback" },
  { icon: "🌍", title: "11 Languages", desc: "Answer in any language you choose" }
];

const STATS = [
  { value: "30+", label: "AI Features" },
  { value: "11", label: "Languages" },
  { value: "100%", label: "Free" },
  { value: "∞", label: "Possibilities" }
];

function FeatureCard({ feature, index, isDark }) {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.1 });
  const border = isDark ? "rgba(99,102,241,0.15)" : "rgba(99,102,241,0.2)";
  const bg = isDark ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.8)";
  const text = isDark ? "#f0f0ff" : "#1a1a2e";
  const subtext = isDark ? "rgba(255,255,255,0.5)" : "#666680";

  return (
    <div
      ref={ref}
      style={{
        padding: "28px",
        borderRadius: "16px",
        background: bg,
        border: `1px solid ${border}`,
        backdropFilter: "blur(10px)",
        transition: "all 0.4s",
        cursor: "pointer",
        opacity: inView ? 1 : 0,
        transform: inView ? "translateY(0)" : "translateY(30px)",
        transitionDelay: `${index * 0.08}s`,
        color: text
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = "translateY(-8px) scale(1.02)";
        e.currentTarget.style.borderColor = "rgba(99,102,241,0.5)";
        e.currentTarget.style.boxShadow = "0 20px 40px rgba(99,102,241,0.15)";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = "translateY(0) scale(1)";
        e.currentTarget.style.borderColor = border;
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div style={{ fontSize: "36px", marginBottom: "12px" }}>{feature.icon}</div>
      <h3 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "8px" }}>{feature.title}</h3>
      <p style={{ color: subtext, fontSize: "13px", lineHeight: "1.6" }}>{feature.desc}</p>
    </div>
  );
}

export default function Home() {
  const [isDark, setIsDark] = useState(true);
  const { ref: heroRef, inView: heroInView } = useInView({ triggerOnce: true });

  const text = isDark ? "#f0f0ff" : "#1a1a2e";
  const subtext = isDark ? "rgba(255,255,255,0.5)" : "#666680";
  const sectionBg = isDark ? "rgba(0,0,0,0.3)" : "rgba(255,255,255,0.4)";
  const cardBorder = isDark ? "rgba(99,102,241,0.2)" : "rgba(99,102,241,0.25)";
  const cardBg = isDark ? "rgba(255,255,255,0.02)" : "rgba(255,255,255,0.7)";

  return (
    <div style={{
      minHeight: "100vh",
      background: isDark
        ? "linear-gradient(135deg, #0a0a0f 0%, #0d0d20 50%, #0a0a0f 100%)"
        : "linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 50%, #f5f0ff 100%)",
      transition: "all 0.5s",
      position: "relative"
    }}>

      {/* Neural Network Background */}
      <NeuralNetwork isDark={isDark} />

      {/* Navbar */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0,
        zIndex: 100,
        padding: "16px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: isDark ? "rgba(10,10,20,0.8)" : "rgba(248,249,255,0.8)",
        backdropFilter: "blur(20px)",
        borderBottom: `1px solid ${isDark ? "rgba(99,102,241,0.15)" : "rgba(99,102,241,0.2)"}`,
        transition: "all 0.5s"
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "38px", height: "38px", borderRadius: "10px",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "20px", boxShadow: "0 0 20px rgba(99,102,241,0.4)"
          }}>🤖</div>
          <span style={{
            fontWeight: "800", fontSize: "22px",
            fontFamily: "Orbitron, sans-serif",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>PVBotX</span>
        </div>

        {/* Nav Links */}
        <div style={{ display: "flex", gap: "4px", alignItems: "center" }}>
          {["Features", "Pricing", "About", "Blog", "Contact"].map(l => (
            <Link key={l} to={`/${l.toLowerCase()}`} style={{
              textDecoration: "none",
              color: subtext,
              fontSize: "14px", fontWeight: "500",
              padding: "6px 14px", borderRadius: "8px",
              transition: "all 0.2s"
            }}
              onMouseEnter={e => e.target.style.color = "#6366f1"}
              onMouseLeave={e => e.target.style.color = subtext}
            >{l}</Link>
          ))}

          {/* Dark/Light Toggle — DOUBLE BUTTON */}
          <div style={{
            display: "flex",
            background: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)",
            borderRadius: "50px",
            padding: "3px",
            border: `1px solid ${cardBorder}`,
            marginLeft: "8px"
          }}>
            <button
              onClick={() => setIsDark(false)}
              style={{
                padding: "5px 14px",
                borderRadius: "50px",
                border: "none",
                background: !isDark ? "white" : "transparent",
                color: !isDark ? "#1a1a2e" : subtext,
                cursor: "pointer",
                fontSize: "13px", fontWeight: "600",
                transition: "all 0.3s",
                boxShadow: !isDark ? "0 2px 8px rgba(0,0,0,0.15)" : "none"
              }}
            >☀️ Light</button>
            <button
              onClick={() => setIsDark(true)}
              style={{
                padding: "5px 14px",
                borderRadius: "50px",
                border: "none",
                background: isDark ? "#1a1a2e" : "transparent",
                color: isDark ? "white" : subtext,
                cursor: "pointer",
                fontSize: "13px", fontWeight: "600",
                transition: "all 0.3s",
                boxShadow: isDark ? "0 2px 8px rgba(0,0,0,0.3)" : "none"
              }}
            >🌙 Dark</button>
          </div>

          <Link to="/chat" style={{ marginLeft: "8px" }}>
            <button style={{
              padding: "9px 22px",
              background: "linear-gradient(135deg, #6366f1, #06b6d4)",
              border: "none", borderRadius: "50px",
              color: "white", cursor: "pointer",
              fontSize: "14px", fontWeight: "600",
              boxShadow: "0 4px 15px rgba(99,102,241,0.4)",
              transition: "all 0.3s"
            }}
              onMouseEnter={e => { e.target.style.transform = "translateY(-2px)"; e.target.style.boxShadow = "0 8px 25px rgba(99,102,241,0.5)"; }}
              onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = "0 4px 15px rgba(99,102,241,0.4)"; }}
            >🚀 Launch App</button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        minHeight: "100vh",
        display: "flex", alignItems: "center", justifyContent: "center",
        textAlign: "center", padding: "120px 24px 80px",
        position: "relative", zIndex: 1
      }}>
        <div
          ref={heroRef}
          style={{
            maxWidth: "900px",
            opacity: heroInView ? 1 : 0,
            transform: heroInView ? "translateY(0)" : "translateY(40px)",
            transition: "all 1s ease"
          }}
        >
          {/* Badge */}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "7px 18px", borderRadius: "50px",
            background: isDark ? "rgba(99,102,241,0.12)" : "rgba(99,102,241,0.08)",
            border: "1px solid rgba(99,102,241,0.3)",
            fontSize: "13px", color: "#6366f1",
            marginBottom: "32px", fontWeight: "500",
            backdropFilter: "blur(10px)"
          }}>
            <span style={{
              width: "7px", height: "7px", borderRadius: "50%",
              background: "#6366f1",
              boxShadow: "0 0 8px #6366f1",
              animation: "livePulse 1.5s ease infinite"
            }} />
            <style>{`
              @keyframes livePulse { 0%,100%{opacity:0.5;transform:scale(0.8)} 50%{opacity:1;transform:scale(1.3)} }
              @keyframes heroFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }
            `}</style>
            Powered by Llama 3.3 • 30+ Features • 100% Free
          </div>

          {/* Main Title */}
          <h1 style={{
            fontSize: "clamp(52px, 9vw, 96px)",
            fontWeight: "900",
            lineHeight: "1.05",
            marginBottom: "24px",
            letterSpacing: "-3px",
            fontFamily: "Orbitron, sans-serif",
            color: text
          }}>
            <span style={{ display: "block" }}>
              Meet{" "}
              <span style={{
                background: "linear-gradient(135deg, #6366f1, #06b6d4, #8b5cf6, #6366f1)",
                backgroundSize: "200%",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                animation: "gradientShift 3s ease infinite"
              }}>PVBotX</span>
            </span>
            <style>{`
              @keyframes gradientShift { 0%,100%{background-position:0%} 50%{background-position:100%} }
            `}</style>
            <span style={{
              fontSize: "clamp(28px, 4.5vw, 52px)",
              fontWeight: "600",
              letterSpacing: "-1px",
              color: subtext,
              fontFamily: "Inter, sans-serif"
            }}>The Future of AI Assistants</span>
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: "clamp(16px, 2.2vw, 20px)",
            color: subtext,
            lineHeight: "1.7",
            marginBottom: "48px",
            maxWidth: "680px",
            margin: "0 auto 48px"
          }}>
            One intelligent chatbox that automatically detects what you need.
            Web search, image generation, code execution, PDF chat and 26 more features —
            all in one place, completely free.
          </p>

          {/* CTA */}
          <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap", marginBottom: "72px" }}>
            <Link to="/chat">
              <button style={{
                padding: "17px 44px",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                border: "none", borderRadius: "50px",
                color: "white", cursor: "pointer",
                fontSize: "17px", fontWeight: "700",
                boxShadow: "0 8px 30px rgba(99,102,241,0.4)",
                transition: "all 0.3s", fontFamily: "Inter, sans-serif"
              }}
                onMouseEnter={e => { e.target.style.transform = "translateY(-3px)"; e.target.style.boxShadow = "0 14px 40px rgba(99,102,241,0.5)"; }}
                onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = "0 8px 30px rgba(99,102,241,0.4)"; }}
              >🚀 Launch PVBotX Free</button>
            </Link>
            <Link to="/features">
              <button style={{
                padding: "17px 44px",
                background: isDark ? "rgba(255,255,255,0.05)" : "rgba(99,102,241,0.06)",
                border: `1px solid ${isDark ? "rgba(255,255,255,0.15)" : "rgba(99,102,241,0.25)"}`,
                borderRadius: "50px",
                color: text, cursor: "pointer",
                fontSize: "17px", fontWeight: "600",
                transition: "all 0.3s", backdropFilter: "blur(10px)",
                fontFamily: "Inter, sans-serif"
              }}
                onMouseEnter={e => { e.target.style.transform = "translateY(-3px)"; e.target.style.borderColor = "rgba(99,102,241,0.5)"; }}
                onMouseLeave={e => { e.target.style.transform = "translateY(0)"; }}
              >✨ See All Features</button>
            </Link>
          </div>

          {/* Stats */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(4,1fr)",
            gap: "24px", maxWidth: "640px", margin: "0 auto"
          }}>
            {STATS.map((s, i) => (
              <div key={i} style={{
                textAlign: "center",
                padding: "16px",
                borderRadius: "12px",
                background: isDark ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.6)",
                border: `1px solid ${cardBorder}`,
                backdropFilter: "blur(10px)"
              }}>
                <div style={{
                  fontSize: "clamp(28px,4vw,40px)", fontWeight: "900",
                  fontFamily: "Orbitron, sans-serif",
                  background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                  WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
                }}>{s.value}</div>
                <div style={{ fontSize: "11px", color: subtext, marginTop: "4px", fontWeight: "500" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section style={{
        padding: "100px 0",
        background: sectionBg,
        backdropFilter: "blur(10px)",
        position: "relative", zIndex: 1
      }}>
        <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "0 24px" }}>
          <h2 style={{
            textAlign: "center",
            fontSize: "clamp(28px,5vw,48px)",
            fontWeight: "800",
            marginBottom: "12px",
            fontFamily: "Orbitron, sans-serif",
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>Everything You Need</h2>
          <p style={{
            textAlign: "center", color: subtext,
            fontSize: "18px", marginBottom: "56px"
          }}>30+ powerful AI features. One smart chatbox. Zero cost.</p>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "20px"
          }}>
            {FEATURES.map((f, i) => (
              <FeatureCard key={i} feature={f} index={i} isDark={isDark} />
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section style={{ padding: "100px 0", position: "relative", zIndex: 1 }}>
        <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "0 24px" }}>
          <h2 style={{
            textAlign: "center",
            fontSize: "clamp(28px,5vw,48px)",
            fontWeight: "800", marginBottom: "12px",
            color: text, fontFamily: "Orbitron, sans-serif"
          }}>How It <span style={{
            background: "linear-gradient(135deg, #6366f1, #06b6d4)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>Works</span></h2>
          <p style={{ textAlign: "center", color: subtext, fontSize: "17px", marginBottom: "60px" }}>
            Just type naturally — PVBotX understands what you need
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px,1fr))", gap: "24px" }}>
            {[
              { step: "01", icon: "💬", title: "Type Anything", desc: "Just describe what you want in plain English" },
              { step: "02", icon: "🧠", title: "AI Detects Mode", desc: "PVBotX automatically detects if you want search, code, image etc." },
              { step: "03", icon: "⚡", title: "Instant Answer", desc: "Get streaming responses with citations and sources" },
              { step: "04", icon: "🔄", title: "Follow Up", desc: "Continue the conversation naturally with full memory" }
            ].map((item, i) => (
              <div key={i} style={{
                padding: "32px 24px",
                borderRadius: "16px",
                background: isDark ? "rgba(255,255,255,0.03)" : "rgba(255,255,255,0.7)",
                border: `1px solid ${cardBorder}`,
                backdropFilter: "blur(10px)",
                textAlign: "center",
                transition: "all 0.3s",
                color: text
              }}
                onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-6px)"; e.currentTarget.style.boxShadow = "0 20px 40px rgba(99,102,241,0.12)"; }}
                onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "none"; }}
              >
                <div style={{
                  fontSize: "11px", fontWeight: "700",
                  color: "#6366f1", marginBottom: "12px",
                  letterSpacing: "2px", fontFamily: "Orbitron, sans-serif"
                }}>STEP {item.step}</div>
                <div style={{ fontSize: "40px", marginBottom: "12px" }}>{item.icon}</div>
                <h3 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "8px" }}>{item.title}</h3>
                <p style={{ color: subtext, fontSize: "13px", lineHeight: "1.6" }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Chat Preview */}
      <section style={{
        padding: "80px 0",
        background: sectionBg,
        backdropFilter: "blur(10px)",
        position: "relative", zIndex: 1
      }}>
        <div style={{ maxWidth: "700px", margin: "0 auto", padding: "0 24px" }}>
          <h2 style={{
            textAlign: "center", fontSize: "32px", fontWeight: "800",
            marginBottom: "40px", color: text, fontFamily: "Orbitron, sans-serif"
          }}>See It In Action</h2>
          <div style={{
            borderRadius: "20px",
            background: isDark ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.85)",
            border: `1px solid ${cardBorder}`,
            backdropFilter: "blur(20px)",
            overflow: "hidden",
            boxShadow: "0 30px 60px rgba(0,0,0,0.2)"
          }}>
            {/* Chat Header */}
            <div style={{
              padding: "14px 20px",
              borderBottom: `1px solid ${cardBorder}`,
              display: "flex", alignItems: "center", gap: "10px",
              background: isDark ? "rgba(255,255,255,0.02)" : "rgba(99,102,241,0.04)"
            }}>
              <div style={{
                width: "32px", height: "32px", borderRadius: "50%",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px"
              }}>🤖</div>
              <span style={{ fontWeight: "600", fontSize: "14px", color: text }}>PVBotX</span>
              <span style={{
                marginLeft: "auto", fontSize: "11px",
                background: "rgba(16,185,129,0.15)",
                border: "1px solid rgba(16,185,129,0.3)",
                color: "#10b981", padding: "2px 10px", borderRadius: "20px"
              }}>● Online</span>
            </div>

            {/* Sample Messages */}
            <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "14px" }}>
              {[
                { role: "user", text: "Generate an image of a futuristic city on Mars" },
                { role: "bot", text: "🖼️ Detected: Image Generation\n\nGenerating your futuristic Mars city... ✅ Done! The image shows towering glass domes, red terrain and Earth visible in the sky.", detected: "Image Generator" },
                { role: "user", text: "Search for latest AI news today" },
                { role: "bot", text: "🔍 Detected: Web Search\n\nFound 8 results for 'latest AI news today'...\n\nTop result: OpenAI releases new model with improved reasoning capabilities...", detected: "Web Search" },
                { role: "user", text: "Write Python code to sort a list of dictionaries" },
                { role: "bot", text: "💻 Detected: Code Interpreter\n\n```python\ndata = [{'name': 'Alice', 'age': 30}]\nsorted_data = sorted(data, key=lambda x: x['age'])\n```\n▶ Output: Sorted successfully!", detected: "Code" }
              ].map((msg, i) => (
                <div key={i} style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  gap: "8px", alignItems: "flex-start"
                }}>
                  {msg.role === "bot" && (
                    <div style={{
                      width: "28px", height: "28px", borderRadius: "50%",
                      background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: "14px", flexShrink: 0
                    }}>🤖</div>
                  )}
                  <div style={{ maxWidth: "75%" }}>
                    {msg.detected && (
                      <div style={{
                        fontSize: "10px", color: "#6366f1", fontWeight: "600",
                        marginBottom: "4px", letterSpacing: "0.5px"
                      }}>AUTO-DETECTED: {msg.detected}</div>
                    )}
                    <div style={{
                      padding: "10px 14px",
                      borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                      background: msg.role === "user"
                        ? "linear-gradient(135deg, rgba(99,102,241,0.3), rgba(139,92,246,0.2))"
                        : (isDark ? "rgba(255,255,255,0.05)" : "rgba(99,102,241,0.05)"),
                      border: `1px solid ${msg.role === "user" ? "rgba(99,102,241,0.3)" : cardBorder}`,
                      color: text, fontSize: "13px", lineHeight: "1.6",
                      whiteSpace: "pre-line"
                    }}>{msg.text}</div>
                  </div>
                  {msg.role === "user" && (
                    <div style={{
                      width: "28px", height: "28px", borderRadius: "50%",
                      background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: "14px", flexShrink: 0
                    }}>🧑</div>
                  )}
                </div>
              ))}
            </div>

            {/* Input Preview */}
            <div style={{
              padding: "12px 16px",
              borderTop: `1px solid ${cardBorder}`,
              display: "flex", gap: "8px", alignItems: "center"
            }}>
              <div style={{
                flex: 1, padding: "8px 14px",
                background: isDark ? "rgba(255,255,255,0.05)" : "rgba(99,102,241,0.05)",
                border: `1px solid ${cardBorder}`,
                borderRadius: "12px",
                fontSize: "13px", color: subtext
              }}>Ask me anything — I detect what you need automatically...</div>
              <div style={{
                width: "34px", height: "34px", borderRadius: "10px",
                background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                color: "white", fontSize: "16px"
              }}>↑</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: "100px 24px", position: "relative", zIndex: 1, textAlign: "center" }}>
        <div style={{
          maxWidth: "700px", margin: "0 auto",
          padding: "72px 40px",
          borderRadius: "24px",
          background: isDark
            ? "linear-gradient(135deg, rgba(99,102,241,0.1), rgba(6,182,212,0.05))"
            : "linear-gradient(135deg, rgba(99,102,241,0.08), rgba(6,182,212,0.04))",
          border: `1px solid ${cardBorder}`,
          backdropFilter: "blur(20px)"
        }}>
          <div style={{ fontSize: "56px", marginBottom: "20px" }}>🚀</div>
          <h2 style={{
            fontSize: "clamp(28px,5vw,42px)", fontWeight: "800",
            marginBottom: "16px", color: text,
            fontFamily: "Orbitron, sans-serif"
          }}>Ready to Experience PVBotX?</h2>
          <p style={{ color: subtext, fontSize: "17px", marginBottom: "40px", lineHeight: "1.6" }}>
            No signup. No credit card. No limits. Just pure AI power.
          </p>
          <Link to="/chat">
            <button style={{
              padding: "18px 52px",
              background: "linear-gradient(135deg, #6366f1, #06b6d4)",
              border: "none", borderRadius: "50px",
              color: "white", cursor: "pointer",
              fontSize: "18px", fontWeight: "700",
              boxShadow: "0 8px 30px rgba(99,102,241,0.4)",
              transition: "all 0.3s", fontFamily: "Inter, sans-serif"
            }}
              onMouseEnter={e => { e.target.style.transform = "translateY(-3px)"; e.target.style.boxShadow = "0 14px 40px rgba(99,102,241,0.5)"; }}
              onMouseLeave={e => { e.target.style.transform = "translateY(0)"; e.target.style.boxShadow = "0 8px 30px rgba(99,102,241,0.4)"; }}
            >🚀 Launch PVBotX — It's Free</button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: "40px 24px",
        borderTop: `1px solid ${cardBorder}`,
        textAlign: "center",
        position: "relative", zIndex: 1,
        background: isDark ? "rgba(0,0,0,0.3)" : "rgba(255,255,255,0.3)",
        backdropFilter: "blur(10px)"
      }}>
        <div style={{
          fontFamily: "Orbitron, sans-serif",
          fontSize: "22px", fontWeight: "700",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          marginBottom: "12px"
        }}>PVBotX</div>
        <p style={{ color: subtext, fontSize: "13px", marginBottom: "20px" }}>
          Built with ❤️ by Pasam Venkata Brahmendra • Powered by Llama 3.3 + Wikipedia + FAISS
        </p>
        <div style={{ display: "flex", gap: "20px", justifyContent: "center", flexWrap: "wrap" }}>
          {["Features", "Pricing", "About", "Blog", "Contact"].map(l => (
            <Link key={l} to={`/${l.toLowerCase()}`} style={{
              color: subtext, textDecoration: "none", fontSize: "13px",
              transition: "color 0.2s"
            }}
              onMouseEnter={e => e.target.style.color = "#6366f1"}
              onMouseLeave={e => e.target.style.color = subtext}
            >{l}</Link>
          ))}
        </div>
        <p style={{ color: subtext, fontSize: "12px", marginTop: "20px", opacity: 0.5 }}>
          © 2025 PVBotX. Open Source on GitHub.
        </p>
      </footer>
    </div>
  );
}