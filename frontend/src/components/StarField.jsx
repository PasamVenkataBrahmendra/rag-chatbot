import { useEffect, useRef } from "react";

export default function StarField() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animId;
    let stars = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const createStars = () => {
      stars = [];
      for (let i = 0; i < 300; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          z: Math.random() * canvas.width,
          pz: 0
        });
      }
    };

    const animate = () => {
      ctx.fillStyle = "rgba(0, 0, 15, 0.15)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      stars.forEach(star => {
        star.pz = star.z;
        star.z -= 2;

        if (star.z <= 0) {
          star.x = Math.random() * canvas.width;
          star.y = Math.random() * canvas.height;
          star.z = canvas.width;
          star.pz = star.z;
        }

        const sx = (star.x - cx) * (canvas.width / star.z) + cx;
        const sy = (star.y - cy) * (canvas.width / star.z) + cy;
        const px = (star.x - cx) * (canvas.width / star.pz) + cx;
        const py = (star.y - cy) * (canvas.width / star.pz) + cy;

        const size = Math.max(0.1, (1 - star.z / canvas.width) * 3);
        const opacity = 1 - star.z / canvas.width;

        ctx.beginPath();
        ctx.strokeStyle = `rgba(${150 + Math.random() * 105}, ${150 + Math.random() * 105}, 255, ${opacity})`;
        ctx.lineWidth = size;
        ctx.moveTo(px, py);
        ctx.lineTo(sx, sy);
        ctx.stroke();
      });

      animId = requestAnimationFrame(animate);
    };

    resize();
    createStars();
    animate();

    window.addEventListener("resize", () => { resize(); createStars(); });

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "fixed",
        top: 0, left: 0,
        width: "100%", height: "100%",
        zIndex: 0,
        pointerEvents: "none"
      }}
    />
  );
}