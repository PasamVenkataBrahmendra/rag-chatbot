import { Link } from "react-router-dom";
import { useInView } from "react-intersection-observer";

const PLANS = [
  {
    name: "Free Forever",
    price: "₹0",
    period: "forever",
    color: "#6366f1",
    popular: false,
    features: [
      "✅ All 30+ AI features",
      "✅ Unlimited chat messages",
      "✅ Web search",
      "✅ PDF chat",
      "✅ Image generation",
      "✅ Code execution",
      "✅ 11 languages",
      "✅ Chat history",
      "✅ Voice input/output",
      "✅ No credit card needed"
    ],
    cta: "Start Free Now",
    link: "/chat"
  },
  {
    name: "Pro",
    price: "Coming Soon",
    period: "",
    color: "#06b6d4",
    popular: true,
    features: [
      "✅ Everything in Free",
      "🔜 Priority processing",
      "🔜 GPT-4o integration",
      "🔜 Custom AI personas",
      "🔜 API access",
      "🔜 Team collaboration",
      "🔜 Analytics dashboard",
      "🔜 Custom domain",
      "🔜 Priority support",
      "🔜 Early access to features"
    ],
    cta: "Join Waitlist",
    link: "/contact"
  }
];

export default function Pricing() {
  const { ref, inView } = useInView({ triggerOnce: true });

  return (
    <div style={{ position: "relative", zIndex: 1, paddingTop: "100px", minHeight: "100vh" }}>
      <div className="container">
        <h1 className="section-title glow-text">Simple Pricing</h1>
        <p className="section-subtitle">
          PVBotX is completely free. No hidden fees, no credit card required.
        </p>

        <div
          ref={ref}
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "32px",
            maxWidth: "800px",
            margin: "0 auto 80px",
            opacity: inView ? 1 : 0,
            transform: inView ? "translateY(0)" : "translateY(40px)",
            transition: "all 0.8s ease"
          }}
        >
          {PLANS.map((plan, i) => (
            <div
              key={i}
              style={{
                padding: "40px 32px",
                borderRadius: "20px",
                background: plan.popular
                  ? "linear-gradient(135deg, rgba(6,182,212,0.1), rgba(99,102,241,0.05))"
                  : "rgba(255,255,255,0.03)",
                border: `1px solid ${plan.popular ? "rgba(6,182,212,0.4)" : "rgba(99,102,241,0.2)"}`,
                position: "relative",
                transform: plan.popular ? "scale(1.02)" : "scale(1)"
              }}
            >
              {plan.popular && (
                <div style={{
                  position: "absolute", top: "-12px", left: "50%",
                  transform: "translateX(-50%)",
                  background: "linear-gradient(135deg, #6366f1, #06b6d4)",
                  padding: "4px 20px", borderRadius: "20px",
                  fontSize: "12px", fontWeight: "600", whiteSpace: "nowrap"
                }}>⭐ Most Popular</div>
              )}
              <h3 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "8px", fontFamily: "Orbitron, sans-serif" }}>
                {plan.name}
              </h3>
              <div style={{
                fontSize: plan.price === "Coming Soon" ? "24px" : "48px",
                fontWeight: "900",
                background: `linear-gradient(135deg, ${plan.color}, #8b5cf6)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                marginBottom: "4px",
                fontFamily: "Orbitron, sans-serif"
              }}>{plan.price}</div>
              {plan.period && <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", marginBottom: "32px" }}>/ {plan.period}</div>}
              {!plan.period && <div style={{ marginBottom: "32px" }} />}
              <ul style={{ listStyle: "none", marginBottom: "32px" }}>
                {plan.features.map((f, j) => (
                  <li key={j} style={{
                    padding: "8px 0",
                    fontSize: "14px",
                    color: f.startsWith("🔜") ? "rgba(255,255,255,0.3)" : "rgba(255,255,255,0.7)",
                    borderBottom: "1px solid rgba(255,255,255,0.04)"
                  }}>{f}</li>
                ))}
              </ul>
              <Link to={plan.link}>
                <button
                  className={plan.popular ? "btn-secondary" : "btn-primary"}
                  style={{ width: "100%", textAlign: "center" }}
                >
                  {plan.cta}
                </button>
              </Link>
            </div>
          ))}
        </div>

        <div style={{
          textAlign: "center",
          padding: "40px",
          borderRadius: "16px",
          background: "rgba(99,102,241,0.05)",
          border: "1px solid rgba(99,102,241,0.1)",
          maxWidth: "600px",
          margin: "0 auto 80px"
        }}>
          <div style={{ fontSize: "32px", marginBottom: "12px" }}>💡</div>
          <h3 style={{ fontSize: "18px", fontWeight: "600", marginBottom: "8px" }}>Why is it free?</h3>
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", lineHeight: "1.7" }}>
            PVBotX was built as a portfolio project to demonstrate advanced AI engineering skills.
            It uses free APIs like Groq (Llama 3.3), Pollinations AI and Wikipedia.
            The entire project is open source on GitHub.
          </p>
        </div>
      </div>
    </div>
  );
}