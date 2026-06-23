import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const links = [
    { to: "/", label: "Home" },
    { to: "/features", label: "Features" },
    { to: "/pricing", label: "Pricing" },
    { to: "/about", label: "About" },
    { to: "/blog", label: "Blog" },
    { to: "/contact", label: "Contact" }
  ];

  return (
    <nav style={{
      position: "fixed",
      top: 0, left: 0, right: 0,
      zIndex: 1000,
      padding: "16px 24px",
      background: scrolled ? "rgba(0,0,15,0.9)" : "transparent",
      backdropFilter: scrolled ? "blur(20px)" : "none",
      borderBottom: scrolled ? "1px solid rgba(99,102,241,0.2)" : "none",
      transition: "all 0.3s",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    }}>
      {/* Logo */}
      <Link to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "10px" }}>
        <div style={{
          width: "40px", height: "40px",
          borderRadius: "12px",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: "20px",
          animation: "pulse-glow 2s ease infinite"
        }}>🤖</div>
        <span style={{
          fontFamily: "Orbitron, sans-serif",
          fontWeight: "700",
          fontSize: "20px",
          background: "linear-gradient(135deg, #6366f1, #06b6d4)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent"
        }}>PVBotX</span>
      </Link>

      {/* Desktop Links */}
      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
        {links.map(l => (
          <Link
            key={l.to}
            to={l.to}
            style={{
              textDecoration: "none",
              color: location.pathname === l.to ? "#6366f1" : "rgba(255,255,255,0.7)",
              fontSize: "14px",
              fontWeight: "500",
              padding: "6px 14px",
              borderRadius: "20px",
              background: location.pathname === l.to ? "rgba(99,102,241,0.1)" : "transparent",
              transition: "all 0.2s"
            }}
          >
            {l.label}
          </Link>
        ))}
        <Link to="/chat">
          <button className="btn-primary" style={{ padding: "8px 20px", fontSize: "13px", marginLeft: "8px" }}>
            Launch App 🚀
          </button>
        </Link>
      </div>
    </nav>
  );
}