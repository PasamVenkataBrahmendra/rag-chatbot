import { useInView } from "react-intersection-observer";
import { Link } from "react-router-dom";

const POSTS = [
  {
    emoji: "🤖",
    cat: "AI",
    title: "What is RAG? How PVBotX Answers Any Question",
    desc: "A deep dive into Retrieval Augmented Generation — how we combine Wikipedia, FAISS and Llama 3 to answer questions accurately.",
    date: "June 2025",
    read: "8 min read"
  },
  {
    emoji: "🔍",
    cat: "Tutorial",
    title: "Building a Web Search AI Like Perplexity",
    desc: "How we integrated the Serper API to give PVBotX real-time internet access and built the web search feature.",
    date: "June 2025",
    read: "6 min read"
  },
  {
    emoji: "💻",
    cat: "Engineering",
    title: "How We Built a Code Interpreter That Actually Runs Code",
    desc: "Safely executing Python code in isolated environments with streaming outputs.",
    date: "June 2025",
    read: "10 min read"
  },
  {
    emoji: "🎓",
    cat: "AI",
    title: "Personal Tutor AI: Teaching Better Than Humans?",
    desc: "Creating interactive lessons, quizzes and follow-up learning experiences.",
    date: "June 2025",
    read: "7 min read"
  },
  {
    emoji: "🚀",
    cat: "Journey",
    title: "From 0 to 30+ Features: Building PVBotX in 6 Weeks",
    desc: "The complete journey from simple RAG chatbot to full AI platform.",
    date: "June 2025",
    read: "12 min read"
  },
  {
    emoji: "🌍",
    cat: "Features",
    title: "11 Languages, One Chatbot",
    desc: "Supporting multilingual AI conversations using Llama 3.",
    date: "June 2025",
    read: "5 min read"
  }
];

function BlogCard({ post, i }) {
  const { ref, inView } = useInView({
    triggerOnce: true
  });

  return (
    <div
      ref={ref}
      style={{
        opacity: inView ? 1 : 0,
        transform: inView
          ? "translateY(0)"
          : "translateY(40px)",
        transition:
          `all .6s ease ${i * .08}s`
      }}
    >
      <div
        style={{
          padding: "28px",

          background:
            "rgba(255,255,255,.03)",

          border:
            "1px solid rgba(99,102,241,.15)",

          borderRadius:
            "20px",

          WebkitBackdropFilter:
            "blur(20px)",

          backdropFilter:
            "blur(20px)",

          minHeight:
            "320px",

          display:
            "flex",

          flexDirection:
            "column",

          justifyContent:
            "space-between",

          transition:
            ".3s"
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform =
            "translateY(-6px)";

          e.currentTarget.style.borderColor =
            "rgba(99,102,241,.45)";
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform =
            "translateY(0)";

          e.currentTarget.style.borderColor =
            "rgba(99,102,241,.15)";
        }}
      >
        <div>

          <div
            style={{
              fontSize:
                "44px",

              marginBottom:
                "16px"
            }}
          >
            {post.emoji}
          </div>

          <div
            style={{
              display:
                "flex",

              gap:
                "10px",

              marginBottom:
                "14px"
            }}
          >
            <span
              style={{
                background:
                  "rgba(99,102,241,.15)",

                color:
                  "#6366f1",

                padding:
                  "4px 10px",

                borderRadius:
                  "20px",

                fontSize:
                  "11px"
              }}
            >
              {post.cat}
            </span>

            <span
              style={{
                color:
                  "rgba(255,255,255,.4)",

                fontSize:
                  "12px"
              }}
            >
              {post.read}
            </span>

          </div>

          <h3
            style={{
              color:
                "#fff",

              marginBottom:
                "12px",

              lineHeight:
                "1.5"
            }}
          >
            {post.title}
          </h3>

          <p
            style={{
              color:
                "rgba(255,255,255,.65)",

              lineHeight:
                "1.8"
            }}
          >
            {post.desc}
          </p>

        </div>

        <Link
          to={`/blog/${i}`}
          style={{
            textDecoration:
              "none",

            marginTop:
              "20px"
          }}
        >
          <button
            className="btn-primary"
          >
            Read More →
          </button>
        </Link>

      </div>
    </div>
  );
}

export default function Blog() {
  return (
    <div
      style={{
        paddingTop:
          "120px",

        minHeight:
          "100vh"
      }}
    >
      <div className="container">

        <h1
          className="section-title glow-text"
        >
          PVBotX Blog
        </h1>

        <p
          className="section-subtitle"
        >
          Deep dives, tutorials and behind-the-scenes engineering stories.
        </p>

        <div
          style={{
            display:
              "grid",

            gridTemplateColumns:
              "repeat(auto-fit,minmax(340px,1fr))",

            gap:
              "24px",

            paddingBottom:
              "80px"
          }}
        >
          {POSTS.map(
            (post, i) => (
              <BlogCard
                key={i}
                post={post}
                i={i}
              />
            )
          )}
        </div>

      </div>
    </div>
  );
}