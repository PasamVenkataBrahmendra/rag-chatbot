import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { useInView } from "react-intersection-observer";

const FEATURES = [
  { icon: "🔍", title: "Web Search", desc: "Real-time internet search like Perplexity AI" },
  { icon: "📄", title: "PDF Chat", desc: "Upload documents and chat with them intelligently" },
  { icon: "🖼️", title: "Image Generation", desc: "Create stunning images from text descriptions" },
  { icon: "💻", title: "Code Interpreter", desc: "Write, explain and execute code in real-time" },
  { icon: "🧮", title: "Math Solver", desc: "Solve complex equations step by step" },
  { icon: "🎓", title: "Personal Tutor", desc: "Learn anything with personalized lessons and quizzes" },
  { icon: "📊", title: "Research Assistant", desc: "Generate full research reports on any topic" },
  { icon: "🎯", title: "Interview Coach", desc: "Practice interviews and get graded feedback" },
  { icon: "🌍", title: "11 Languages", desc: "Answer in English, Hindi, Spanish and 8 more" }
];

const STATS = [
  { value: "23+", label: "AI Features" },
  { value: "11", label: "Languages" },
  { value: "100%", label: "Free to Use" },
  { value: "∞", label: "Possibilities" }
];

function FeatureCard({ feature, index }) {
  const { ref, inView } = useInView({ triggerOnce: true, threshold: 0.1 });

  return (
    <div
      ref={ref}
      style={{
        padding: "28px",
        borderRadius: "16px",
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(99,102,241,0.15)",
        transition: "all 0.4s",
        cursor: "pointer",
        opacity: inView ? 1 : 0,
        transform: inView ? "translateY(0)" : "translateY(30px)",
        transitionDelay: `${index * 0.1}s`
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = "translateY(-8px)";
        e.currentTarget.style.borderColor = "rgba(99,102,241,0.5)";
        e.currentTarget.style.boxShadow = "0 20px 40px rgba(99,102,241,0.15)";
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "rgba(99,102,241,0.15)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div style={{ fontSize: "36px", marginBottom: "12px" }}>{feature.icon}</div>
      <h3 style={{ fontSize: "16px", fontWeight: "600", marginBottom: "8px" }}>{feature.title}</h3>
      <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "13px", lineHeight: "1.6" }}>{feature.desc}</p>
    </div>
  );
}

export default function Home() {
  const { ref: heroRef, inView: heroInView } = useInView({ triggerOnce: true });

  return (
    <div style={{ position: "relative", zIndex: 1 }}>

      {/* Hero Section */}
      <section style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "120px 24px 80px" }}>
        <div ref={heroRef} style={{ maxWidth: "900px", opacity: heroInView ? 1 : 0, transform: heroInView ? "translateY(0)" : "translateY(40px)", transition: "all 1s ease" }}>

          {/* Badge */}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "6px 16px", borderRadius: "50px",
            background: "rgba(99,102,241,0.1)",
            border: "1px solid rgba(99,102,241,0.3)",
            fontSize: "13px", color: "#6366f1",
            marginBottom: "32px", fontWeight: "500"
          }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#6366f1", animation: "pulse-glow 1s infinite" }}/>
            Powered by Llama 3.3 • Free Forever
          </div>

          {/* Title */}
          <h1 style={{
            fontSize: "clamp(48px, 8vw, 88px)",
            fontWeight: "900",
            lineHeight: "1.1",
            marginBottom: "24px",
            letterSpacing: "-2px"
          }}>
            <span style={{
              background: "linear-gradient(135deg, #ffffff, #8888aa)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}>Meet </span>
            <span style={{
              background: "linear-gradient(135deg, #6366f1, #06b6d4, #8b5cf6)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              animation: "pulse-glow 3s ease infinite"
            }}>PVBotX</span>
            <br />
            <span style={{
              background: "linear-gradient(135deg, #ffffff, #8888aa)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontSize: "clamp(32px, 5vw, 56px)"
            }}>The Future of AI</span>
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: "clamp(16px, 2.5vw, 20px)",
            color: "rgba(255,255,255,0.5)",
            lineHeight: "1.7",
            marginBottom: "48px",
            maxWidth: "700px",
            margin: "0 auto 48px"
          }}>
            The most feature-rich AI chatbot ever built. 23+ features including web search,
            PDF chat, image generation, code execution, personal tutor and much more.
            All completely free.
          </p>

          {/* CTA Buttons */}
          <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap", marginBottom: "80px" }}>
            <Link to="/chat">
              <button className="btn-primary" style={{ fontSize: "16px", padding: "16px 40px" }}>
                🚀 Launch PVBotX Free
              </button>
            </Link>
            <Link to="/features">
              <button className="btn-secondary" style={{ fontSize: "16px", padding: "16px 40px" }}>
                ✨ See All Features
              </button>
            </Link>
          </div>

          {/* Stats */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "24px",
            maxWidth: "700px",
            margin: "0 auto"
          }}>
            {STATS.map((s, i) => (
              <div key={i} style={{ textAlign: "center" }}>
                <div style={{
                  fontSize: "clamp(28px, 4vw, 40px)",
                  fontWeight: "800",
                  fontFamily: "Orbitron, sans-serif",
                  background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent"
                }}>{s.value}</div>
                <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", marginTop: "4px" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Floating Robot */}
      <div style={{
        position: "absolute",
        top: "15%",
        right: "5%",
        fontSize: "120px",
        animation: "float 4s ease-in-out infinite",
        zIndex: 0,
        opacity: 0.15,
        pointerEvents: "none"
      }}>🤖</div>

      {/* Features Grid */}
      <section className="section" style={{ background: "rgba(0,0,0,0.3)" }}>
        <div className="container">
          <h2 className="section-title glow-text">Everything You Need</h2>
          <p className="section-subtitle">
            23+ powerful AI features in one place. No switching between tools.
          </p>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "20px"
          }}>
            {FEATURES.map((f, i) => <FeatureCard key={i} feature={f} index={i} />)}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="container" style={{ textAlign: "center" }}>
          <div style={{
            padding: "80px 40px",
            borderRadius: "24px",
            background: "linear-gradient(135deg, rgba(99,102,241,0.1), rgba(6,182,212,0.05))",
            border: "1px solid rgba(99,102,241,0.2)",
            position: "relative",
            overflow: "hidden"
          }}>
            <div style={{
              position: "absolute", top: "-50%", left: "-50%",
              width: "200%", height: "200%",
              background: "radial-gradient(ellipse at center, rgba(99,102,241,0.05) 0%, transparent 60%)",
              pointerEvents: "none"
            }}/>
            <h2 style={{ fontSize: "clamp(28px, 5vw, 48px)", fontWeight: "900", marginBottom: "16px" }}>
              Ready to Experience the Future?
            </h2>
            <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "18px", marginBottom: "40px" }}>
              Join thousands of users who have already discovered PVBotX
            </p>
            <Link to="/chat">
              <button className="btn-primary" style={{ fontSize: "18px", padding: "18px 48px" }}>
                🚀 Start for Free — No Signup Needed
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        padding: "48px 24px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        textAlign: "center"
      }}>
        <div style={{
          fontFamily: "Orbitron, sans-serif",
          fontSize: "24px",
          fontWeight: "700",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          marginBottom: "16px"
        }}>PVBotX</div>
        <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "13px", marginBottom: "24px" }}>
          Built with ❤️ by Pasam Venkata Brahmendra • Powered by Llama 3.3 + Wikipedia + FAISS
        </p>
        <div style={{ display: "flex", gap: "24px", justifyContent: "center", flexWrap: "wrap" }}>
          {["Home", "Features", "Pricing", "About", "Blog", "Contact"].map(l => (
            <Link key={l} to={`/${l.toLowerCase()}`} style={{ color: "rgba(255,255,255,0.4)", textDecoration: "none", fontSize: "13px" }}>
              {l}
            </Link>
          ))}
        </div>
        <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "12px", marginTop: "24px" }}>
          © 2025 PVBotX. All rights reserved.
        </p>
      </footer>
    </div>
  );
}