import { useInView } from "react-intersection-observer";
import { Link } from "react-router-dom";

const ALL_FEATURES = [
{ icon:"💬", title:"Smart Chat", desc:"Wikipedia-powered RAG chat", badge:"Core" },
{ icon:"🔍", title:"Web Search", desc:"Real-time internet answers", badge:"Live" },
{ icon:"🖼️", title:"Image Generation", desc:"Generate images instantly", badge:"Free" },
{ icon:"📄", title:"PDF Chat", desc:"Ask questions on PDFs", badge:"Smart" },
{ icon:"📚", title:"Multi PDF", desc:"Chat with multiple PDFs", badge:"Pro" },
{ icon:"🖼️", title:"Image Understanding", desc:"Upload and analyze images", badge:"Vision" },
{ icon:"▶️", title:"YouTube Chat", desc:"Chat with videos", badge:"Unique" },
{ icon:"🌐", title:"Website Chat", desc:"Understand websites", badge:"Unique" },
{ icon:"💻", title:"Code Interpreter", desc:"Execute Python", badge:"Execute" },
{ icon:"🧮", title:"Math Solver", desc:"Step-by-step solutions", badge:"Smart" },
{ icon:"📊", title:"Research Assistant", desc:"Generate reports", badge:"Unique" },
{ icon:"🗺️", title:"Learning Path", desc:"Personalized roadmaps", badge:"Unique" },
{ icon:"🎯", title:"Interview Coach", desc:"Practice interviews", badge:"Career" },
{ icon:"📋", title:"Resume Analyzer", desc:"ATS score & feedback", badge:"Career" },
{ icon:"🎓", title:"Personal Tutor", desc:"Interactive learning", badge:"Smart" },
{ icon:"🃏", title:"Flashcards", desc:"Generate study cards", badge:"Smart" },
{ icon:"📝", title:"Quiz Mode", desc:"MCQ quizzes", badge:"Smart" },
{ icon:"🗄️", title:"Text to SQL", desc:"English → SQL", badge:"Dev" },
{ icon:"📐", title:"Diagram Generator", desc:"Generate diagrams", badge:"Dev" },
{ icon:"📧", title:"Email Writer", desc:"Write professional emails", badge:"Writing" },
{ icon:"📄", title:"Cover Letter", desc:"Tailored applications", badge:"Writing" },
{ icon:"✅", title:"Grammar Checker", desc:"Improve writing", badge:"Writing" },
{ icon:"🎨", title:"Tone Changer", desc:"Rewrite tone", badge:"Writing" },
{ icon:"🧠", title:"Mind Map", desc:"Visual idea mapping", badge:"Visual" },
{ icon:"🎯", title:"Action Plan", desc:"Goal planning", badge:"Smart" },
{ icon:"⚔️", title:"Debate Mode", desc:"Arguments for both sides", badge:"Unique" },
{ icon:"🌍", title:"11 Languages", desc:"Multilingual AI", badge:"Global" },
{ icon:"💾", title:"Chat History", desc:"SQLite persistence", badge:"Persist" },
{ icon:"🎙️", title:"Voice Input", desc:"Speech questions", badge:"New" },
{ icon:"🔊", title:"Text to Speech", desc:"Hear responses", badge:"New" }
];

const COLORS = {
Core:"#6366f1",
Live:"#10b981",
Free:"#f59e0b",
Smart:"#8b5cf6",
Pro:"#7c3aed",
Vision:"#06b6d4",
Unique:"#ec4899",
Execute:"#f97316",
Career:"#10b981",
Dev:"#06b6d4",
Writing:"#8b5cf6",
Visual:"#f59e0b",
Global:"#0ea5e9",
Persist:"#6366f1",
New:"#ef4444"
};

function Card({ item, i }) {
const { ref, inView } =
useInView({
triggerOnce:true
});

return (
<div
ref={ref}
style={{
padding:"28px",
borderRadius:"20px",
background:"rgba(255,255,255,.04)",
border:"1px solid rgba(99,102,241,.2)",
WebkitBackdropFilter:"blur(18px)",
backdropFilter:"blur(18px)",
minHeight:"240px",
opacity:inView?1:0,
transform:
inView
?"translateY(0)"
:"translateY(40px)",
transition:
`all .5s ease ${i*.03}s`
}}
>

<div
style={{
display:"inline-block",
padding:"4px 10px",
borderRadius:"999px",
fontSize:"11px",
marginBottom:"18px",
color:
COLORS[item.badge],
background:
`${COLORS[item.badge]}22`
}}
>
{item.badge}
</div>

<div
style={{
fontSize:"42px",
marginBottom:"18px"
}}
>
{item.icon}
</div>

<h3
style={{
marginBottom:"12px",
color:"#fff"
}}
>
{item.title}
</h3>

<p
style={{
color:
"rgba(255,255,255,.7)",
lineHeight:1.8
}}
>
{item.desc}
</p>

</div>
);
}

export default function Features() {
return (
<div
style={{
paddingTop:"110px"
}}
>

<div className="container">

<h1
className="section-title glow-text"
>
{ALL_FEATURES.length}+ AI Features
</h1>

<p
className="section-subtitle"
>
Everything available inside PVBotX
</p>

<div
style={{
display:"grid",
gridTemplateColumns:
"repeat(auto-fit,minmax(280px,1fr))",
gap:"20px"
}}
>
{ALL_FEATURES.map(
(item,i)=>(
<Card
key={i}
item={item}
i={i}
/>
)
)}
</div>

<div
style={{
textAlign:"center",
padding:"80px 0"
}}
>
<Link to="/chat">
<button
className="btn-primary"
>
🚀 Launch PVBotX
</button>
</Link>
</div>

</div>

</div>
);
}