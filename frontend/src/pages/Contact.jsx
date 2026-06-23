import { useState } from "react";
import { useInView } from "react-intersection-observer";

export default function Contact() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });

  const [sent, setSent] = useState(false);

  const { ref, inView } = useInView({
    triggerOnce: true
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // TODO: Connect backend/email service
    setSent(true);

    setForm({
      name: "",
      email: "",
      subject: "",
      message: ""
    });
  };

  const CONTACTS = [
    {
      icon: "📧",
      label: "Email",
      value: "pvbrahmendra@gmail.com",
      link: "mailto:pvbrahmendra@gmail.com"
    },
    {
      icon: "💼",
      label: "GitHub",
      value: "PasamVenkataBrahmendra",
      link: "https://github.com/PasamVenkataBrahmendra/rag-chatbot"
    },
    {
      icon: "🤖",
      label: "PVBotX",
      value: "Try it now",
      link: "/chat"
    }
  ];

  return (
    <div
      style={{
        position: "relative",
        zIndex: 1,
        paddingTop: "100px",
        minHeight: "100vh"
      }}
    >
      <div className="container">

        <h1 className="section-title glow-text">
          Get In Touch
        </h1>

        <p className="section-subtitle">
          Have questions, feedback or want to collaborate?
          I'd love to hear from you.
        </p>

        <div
          ref={ref}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1.5fr",
            gap: "48px",
            maxWidth: "900px",
            margin: "0 auto 80px",
            opacity: inView ? 1 : 0,
            transform: inView
              ? "translateY(0)"
              : "translateY(40px)",
            transition: "all 0.8s ease"
          }}
        >

          {/* LEFT */}
          <div>

            <h2
              style={{
                fontSize: "24px",
                fontWeight: "700",
                marginBottom: "16px"
              }}
            >
              Let's Connect
            </h2>

            <p
              style={{
                color: "rgba(255,255,255,0.5)",
                lineHeight: "1.7",
                marginBottom: "32px"
              }}
            >
              Whether you're interested in the project,
              want to report a bug,
              or have a job opportunity —
              feel free to reach out.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "16px"
              }}
            >
              {CONTACTS.map((c, i) => (
                <a
                  key={i}
                  href={c.link}
                  target={
                    c.link.startsWith("http")
                      ? "_blank"
                      : "_self"
                  }
                  rel="noreferrer"
                  style={{
                    textDecoration: "none"
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "14px",
                      padding: "16px",
                      borderRadius: "12px",
                      background:
                        "rgba(255,255,255,0.03)",
                      border:
                        "1px solid rgba(99,102,241,0.15)",
                      transition: "all 0.3s"
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor =
                        "rgba(99,102,241,0.4)";
                      e.currentTarget.style.background =
                        "rgba(99,102,241,0.05)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor =
                        "rgba(99,102,241,0.15)";
                      e.currentTarget.style.background =
                        "rgba(255,255,255,0.03)";
                    }}
                  >
                    <span
                      style={{
                        fontSize: "24px"
                      }}
                    >
                      {c.icon}
                    </span>

                    <div>
                      <div
                        style={{
                          fontSize: "12px",
                          color:
                            "rgba(255,255,255,0.4)"
                        }}
                      >
                        {c.label}
                      </div>

                      <div
                        style={{
                          fontSize: "14px",
                          color: "#6366f1",
                          fontWeight: "500"
                        }}
                      >
                        {c.value}
                      </div>
                    </div>
                  </div>
                </a>
              ))}
            </div>

          </div>

          {/* RIGHT */}
          <div
            style={{
              padding: "40px",
              borderRadius: "20px",
              background:
                "rgba(255,255,255,0.02)",
              border:
                "1px solid rgba(99,102,241,0.15)"
            }}
          >
            {sent ? (
              <div
                style={{
                  textAlign: "center",
                  padding: "40px 0"
                }}
              >
                <div
                  style={{
                    fontSize: "64px",
                    marginBottom: "16px"
                  }}
                >
                  ✅
                </div>

                <h3>
                  Message Sent!
                </h3>

                <p
                  style={{
                    color:
                      "rgba(255,255,255,0.5)"
                  }}
                >
                  Thanks for reaching out.
                  I'll get back to you soon.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>

                {[
                  ["name", "Your Name", "text"],
                  ["email", "Email Address", "email"],
                  ["subject", "Subject", "text"]
                ].map(([key, label, type]) => (
                  <div
                    key={key}
                    style={{
                      marginBottom: "20px"
                    }}
                  >
                    <label>
                      {label}
                    </label>

                    <input
                      type={type}
                      value={form[key]}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          [key]:
                            e.target.value
                        })
                      }
                      required
                      style={{
                        width: "100%",
                        padding: "12px"
                      }}
                    />
                  </div>
                ))}

                <textarea
                  rows={5}
                  value={form.message}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      message:
                        e.target.value
                    })
                  }
                  placeholder="Your message..."
                  required
                  style={{
                    width: "100%",
                    padding: "12px",
                    marginBottom: "20px"
                  }}
                />

                <button
                  type="submit"
                  className="btn-primary"
                  style={{
                    width: "100%"
                  }}
                >
                  📩 Send Message
                </button>

              </form>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}