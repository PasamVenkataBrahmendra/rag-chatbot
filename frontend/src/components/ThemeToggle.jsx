import { useEffect, useState } from "react";

export default function ThemeToggle() {

const [dark,setDark]=useState(
localStorage.getItem("theme")
!== "light"
);

useEffect(()=>{

document.documentElement.setAttribute(
"data-theme",
dark ? "dark":"light"
);

localStorage.setItem(
"theme",
dark ? "dark":"light"
);

},[dark]);

return (

<button

onClick={()=>
setDark(!dark)
}

style={{

width:"56px",

height:"32px",

borderRadius:"999px",

border:"none",

cursor:"pointer",

background:
dark
?
"linear-gradient(135deg,#6366f1,#06b6d4)"
:
"#ddd",

position:"relative",

transition:".3s"

}}

>

<div

style={{

position:"absolute",

top:"3px",

left:
dark
?
"28px"
:
"3px",

width:"26px",

height:"26px",

borderRadius:"50%",

background:"#fff",

display:"flex",

alignItems:"center",

justifyContent:"center",

transition:".3s"

}}

>

{dark ? "🌙":"☀️"}

</div>

</button>

);

}