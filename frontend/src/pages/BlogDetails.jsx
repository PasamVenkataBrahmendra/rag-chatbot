import { useParams } from "react-router-dom";

const BLOGS = {
  0: {
    title:
      "What is RAG? How PVBotX Answers Any Question",

    content:
      `
RAG means Retrieval Augmented Generation.

PVBotX retrieves information
from external knowledge sources.

Flow:

1. User asks question

2. Relevant chunks retrieved

3. Context sent to LLM

4. Final answer generated

Stack:

• FAISS
• SBERT
• FastAPI
• Llama 3
`
  },

  1: {
    title:
      "Building a Web Search AI",

    content:
      `
Search systems combine:

• Query generation

• Search engine

• Ranking

• Context injection

This allows real-time answers.
`
  },

  2: {
    title:
      "Code Interpreter",

    content:
      `
Code execution occurs
inside isolated environments.

Features:

• Execute

• Debug

• Stream outputs
`
  },

  3: {
    title:
      "Personal Tutor AI",

    content:
      `
Structured learning.

Lessons.

Quizzes.

Adaptive teaching.
`
  },

  4: {
    title:
      "0 → 30 Features",

    content:
      `
Started from RAG.

Expanded into:

PDF

Vision

Research

Tutor

Voice.
`
  },

  5: {
    title:
      "11 Language Support",

    content:
      `
Multilingual prompting.

Translation.

Context preservation.
`
  }
};

export default function BlogDetails() {

  const { id } =
    useParams();

  const blog =
    BLOGS[id];

  if (!blog) {
    return (
      <div
        style={{
          paddingTop:
            "140px",

          textAlign:
            "center"
        }}
      >
        Blog not found
      </div>
    );
  }

  return (
    <div
      style={{
        paddingTop:
          "120px"
      }}
    >
      <div className="container">

        <h1
          className="section-title glow-text"
        >
          {blog.title}
        </h1>

        <div
          className="glass"
          style={{
            padding:
              "40px",

            borderRadius:
              "20px",

            whiteSpace:
              "pre-line",

            lineHeight:
              "2"
          }}
        >
          {blog.content}
        </div>

      </div>
    </div>
  );
}