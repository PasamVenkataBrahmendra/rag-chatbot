import { useInView } from "react-intersection-observer";
import { Link } from "react-router-dom";

const TECH = [
  { icon: "🐍", name: "Python", desc: "Core language" },
  { icon: "⚛️", name: "React", desc: "Frontend UI" },
  { icon: "🚀", name: "FastAPI", desc: "REST API" },
  { icon: "🤖", name: "Llama 3.3", desc: "LLM via Groq" },
  { icon: "🔍", name: "FAISS", desc: "Vector search" },
  { icon: "🧠", name: "SBERT", desc: "Embeddings" },
  { icon: "📦", name: "SQLite", desc: "Persistence" },
  { icon: "🌐", name: "Wikipedia", desc: "Knowledge base" }
];

export default function About() {
  const { ref, inView } = useInView({
    triggerOnce: true
  });

  return (
    <div
      style={{
        position: "relative",
        zIndex: 1,
        paddingTop: "100px"
      }}
    >
      <div className="container">

        {/* Hero */}
        <div
          style={{
            textAlign: "center",
            marginBottom: "80px"
          }}
        >
          <div
            style={{
              fontSize: "80px",
              marginBottom: "24px",
              animation: "float 4s ease-in-out infinite"
            }}
          >
            🤖
          </div>

          <h1 className="section-title glow-text">
            About PVBotX
          </h1>

          <p className="section-subtitle">
            Built by a passionate developer to demonstrate the future of AI assistants
          </p>
        </div>

        {/* Story */}
        <div
          ref={ref}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "60px",
            marginBottom: "80px",
            opacity: inView ? 1 : 0,
            transform: inView
              ? "translateY(0)"
              : "translateY(40px)",
            transition: "all 0.8s ease"
          }}
        >
          <div>
            <h2
              style={{
                fontSize: "32px",
                fontWeight: "700",
                marginBottom: "20px"
              }}
            >
              The Story Behind{" "}
              <span className="glow-text">
                PVBotX
              </span>
            </h2>

            <p
              style={{
                color: "rgba(255,255,255,0.6)",
                lineHeight: "1.8",
                marginBottom: "16px"
              }}
            >
              PVBotX was created by{" "}
              <strong style={{ color: "#6366f1" }}>
                Pasam Venkata Brahmendra
              </strong>{" "}
              as a portfolio project to showcase advanced AI engineering skills including
              RAG pipelines, vector databases,
              LLM integration and full-stack development.
            </p>

            <p
              style={{
                color: "rgba(255,255,255,0.6)",
                lineHeight: "1.8",
                marginBottom: "16px"
              }}
            >
              Starting from a simple Q&A chatbot,
              it evolved into a comprehensive AI platform
              with 30+ features that rivals commercial products.
            </p>

            <p
              style={{
                color: "rgba(255,255,255,0.6)",
                lineHeight: "1.8"
              }}
            >
              The project demonstrates expertise in NLP,
              transformer models, vector search,
              REST APIs, React development and deployment.
            </p>
          </div>

          <div
            style={{
              padding: "40px",
              borderRadius: "20px",
              background: "rgba(99,102,241,0.05)",
              border: "1px solid rgba(99,102,241,0.2)"
            }}
          >
            <h3
              style={{
                fontSize: "20px",
                fontWeight: "600",
                marginBottom: "24px"
              }}
            >
              👨‍💻 The Developer
            </h3>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "16px",
                marginBottom: "20px"
              }}
            >
              <div
                style={{
                  width: "60px",
                  height: "60px",
                  borderRadius: "50%",
                  background:
                    "linear-gradient(135deg,#6366f1,#06b6d4)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "28px"
                }}
              >
                P
              </div>

              <div>
                <div
                  style={{
                    fontWeight: "600"
                  }}
                >
                  Pasam Venkata Brahmendra
                </div>

                <div
                  style={{
                    color: "rgba(255,255,255,0.4)",
                    fontSize: "13px"
                  }}
                >
                  AI/ML Engineer • Full Stack Developer
                </div>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px"
              }}
            >
              {[
                "🎓 Computer Science Graduate",
                "🤖 Specializes in NLP & LLMs",
                "💻 Python & React Developer",
                "📊 ML/AI Portfolio Projects",
                "🚀 Open to Job Opportunities"
              ].map((item, i) => (
                <div
                  key={i}
                  style={{
                    color: "rgba(255,255,255,0.6)",
                    fontSize: "14px"
                  }}
                >
                  {item}
                </div>
              ))}
            </div>

            <Link to="/contact">
              <button
                className="btn-primary"
                style={{
                  width: "100%",
                  marginTop: "24px"
                }}
              >
                📩 Get In Touch
              </button>
            </Link>
          </div>
        </div>

        {/* Tech Stack */}
        <div style={{ marginBottom: "80px" }}>
          <h2
            style={{
              textAlign: "center",
              fontSize: "32px",
              marginBottom: "40px"
            }}
          >
            Built With{" "}
            <span className="glow-text">
              Cutting-Edge Tech
            </span>
          </h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(140px,1fr))",
              gap: "16px"
            }}
          >
            {TECH.map((t, i) => (
              <div
                key={i}
                style={{
                  padding: "24px",
                  borderRadius: "12px",
                  background: "rgba(255,255,255,0.03)",
                  border:
                    "1px solid rgba(99,102,241,0.1)",
                  textAlign: "center"
                }}
              >
                <div
                  style={{
                    fontSize: "28px",
                    marginBottom: "8px"
                  }}
                >
                  {t.icon}
                </div>

                <div
                  style={{
                    fontWeight: "600"
                  }}
                >
                  {t.name}
                </div>

                <div
                  style={{
                    color: "rgba(255,255,255,0.4)",
                    fontSize: "12px"
                  }}
                >
                  {t.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* GitHub */}
        <div
          style={{
            textAlign: "center",
            paddingBottom: "80px"
          }}
        >
          <div
            style={{
              padding: "48px",
              borderRadius: "20px",
              background:
                "rgba(255,255,255,0.02)",
              border:
                "1px solid rgba(255,255,255,0.08)",
              maxWidth: "600px",
              margin: "0 auto"
            }}
          >
            <div
              style={{
                fontSize: "48px",
                marginBottom: "16px"
              }}
            >
              ⭐
            </div>

            <h3
              style={{
                fontSize: "24px",
                marginBottom: "12px"
              }}
            >
              Open Source on GitHub
            </h3>

            <p
              style={{
                color: "rgba(255,255,255,0.5)",
                marginBottom: "24px"
              }}
            >
              PVBotX is completely open source.
              Star the repo, fork it, learn from it.
            </p>

            <a
              href="https://github.com/PasamVenkataBrahmendra/rag-chatbot"
              target="_blank"
              rel="noreferrer"
              className="btn-primary"
              style={{
                display: "inline-block",
                textDecoration: "none"
              }}
            >
              ⭐ Star on GitHub
            </a>
          </div>
        </div>

      </div>
    </div>
  );
}