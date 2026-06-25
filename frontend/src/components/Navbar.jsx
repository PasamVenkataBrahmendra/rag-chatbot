import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () =>
      setScrolled(window.scrollY > 50);

    window.addEventListener(
      "scroll",
      onScroll
    );

    return () =>
      window.removeEventListener(
        "scroll",
        onScroll
      );
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
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,

        zIndex: 1000,

        padding: "14px 26px",

        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",

        background: scrolled
          ? "rgba(5,5,20,.88)"
          : "rgba(5,5,20,.35)",

        backdropFilter:
          "blur(18px)",

        borderBottom:
          "1px solid rgba(99,102,241,.12)"
      }}
    >
      {/* Logo */}

      <Link
        to="/"
        style={{
          textDecoration: "none",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          flexShrink: 0
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,

            borderRadius: 14,

            background:
              "linear-gradient(135deg,#6366f1,#06b6d4)",

            display: "flex",

            alignItems: "center",

            justifyContent: "center",

            fontSize: 22
          }}
        >
          🤖
        </div>

        <span
          style={{
            fontSize: 22,

            fontWeight: 700,

            fontFamily:
              "Orbitron",

            background:
              "linear-gradient(135deg,#6366f1,#06b6d4)",

            WebkitBackgroundClip:
              "text",

            WebkitTextFillColor:
              "transparent"
          }}
        >
          PVBotX
        </span>
      </Link>

      {/* CENTER LINKS */}

      <div
        style={{
          display: "flex",

          gap: "6px",

          alignItems: "center",

          flexWrap: "wrap",

          justifyContent:
            "center",

          margin:
            "0 30px",

          flex: 1
        }}
      >
        {links.map(link => (
          <Link
            key={link.to}
            to={link.to}
            style={{
              textDecoration:
                "none",

              color:
                location.pathname ===
                link.to
                  ? "#6366f1"
                  : "rgba(255,255,255,.75)",

              padding:
                "8px 14px",

              borderRadius:
                "999px",

              whiteSpace:
                "nowrap",

              fontSize:
                "14px",

              background:
                location.pathname ===
                link.to
                  ? "rgba(99,102,241,.12)"
                  : "transparent"
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>

      {/* RIGHT */}

      <div
        style={{
          display: "flex",

          alignItems:
            "center",

          gap: "12px",

          flexShrink: 0
        }}
      >
        <ThemeToggle />

        <Link
          to="/chat"
        >
          <button
            style={{
              border: "none",

              padding:
                "12px 22px",

              borderRadius:
                "999px",

              color:
                "#fff",

              fontWeight:
                "700",

              cursor:
                "pointer",

              background:
                "linear-gradient(135deg,#6366f1,#06b6d4)"
            }}
          >
            Launch App 🚀
          </button>
        </Link>
      </div>
    </nav>
  );
}