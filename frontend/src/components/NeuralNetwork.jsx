import { useEffect, useRef } from "react";

export default function NeuralNetwork({ isDark }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    let animId;
    let nodes = [];

    let mouse = {
      x: -9999,
      y: -9999
    };

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      createNodes();
    };

    const createNodes = () => {
      nodes = [];

      const count = Math.max(
        50,
        Math.floor(
          (canvas.width * canvas.height) /
          12000
        )
      );

      for (let i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,

          vx:
            (Math.random() - 0.5) *
            0.4,

          vy:
            (Math.random() - 0.5) *
            0.4,

          radius:
            Math.random() * 3 + 1,

          pulse:
            Math.random() *
            Math.PI *
            2,

          pulseSpeed:
            Math.random() *
              0.02 +
            0.01,

          color:
            Math.random() > 0.5
              ? "99,102,241"
              : "6,182,212"
        });
      }
    };

    const onMouseMove = e => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    const animate = () => {
      ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
      );

      ctx.fillStyle =
        isDark
          ? "rgba(10,10,20,0.15)"
          : "rgba(248,249,255,0.15)";

      ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
      );

      nodes.forEach(
        (node, i) => {

          node.x += node.vx;
          node.y += node.vy;

          node.pulse +=
            node.pulseSpeed;

          if (
            node.x < 0 ||
            node.x > canvas.width
          ) {
            node.vx *= -1;
          }

          if (
            node.y < 0 ||
            node.y > canvas.height
          ) {
            node.vy *= -1;
          }

          const dx =
            mouse.x -
            node.x;

          const dy =
            mouse.y -
            node.y;

          const dist =
            Math.sqrt(
              dx * dx +
              dy * dy
            );

          if (dist < 150) {
            node.vx +=
              dx *
              0.00015;

            node.vy +=
              dy *
              0.00015;
          }

          const speed =
            Math.sqrt(
              node.vx *
                node.vx +
                node.vy *
                node.vy
            );

          if (speed > 1.5) {
            node.vx *= 0.99;
            node.vy *= 0.99;
          }

          nodes.forEach(
            (other, j) => {

              if (j <= i)
                return;

              const dx =
                other.x -
                node.x;

              const dy =
                other.y -
                node.y;

              const d =
                Math.sqrt(
                  dx *
                    dx +
                    dy *
                    dy
                );

              const maxDist =
                120;

              if (
                d <
                maxDist
              ) {

                const opacity =
                  (
                    1 -
                    d /
                      maxDist
                  ) *
                  0.4;

                const gradient =
                  ctx.createLinearGradient(
                    node.x,
                    node.y,
                    other.x,
                    other.y
                  );

                gradient.addColorStop(
                  0,
                  `rgba(${node.color},${opacity})`
                );

                gradient.addColorStop(
                  1,
                  `rgba(${other.color},${opacity})`
                );

                ctx.beginPath();

                ctx.strokeStyle =
                  gradient;

                ctx.lineWidth =
                  opacity *
                  1.5;

                ctx.moveTo(
                  node.x,
                  node.y
                );

                ctx.lineTo(
                  other.x,
                  other.y
                );

                ctx.stroke();
              }
            }
          );

          // SAFE GLOW

          const pulseSize =
            Math.max(
              1,
              node.radius +
                Math.sin(
                  node.pulse
                ) *
                  1.2
            );

          const glowRadius =
            Math.max(
              4,
              pulseSize * 4
            );

          const opacity =
            isDark
              ? 0.8
              : 0.6;

          const glow =
            ctx.createRadialGradient(
              node.x,
              node.y,
              0,
              node.x,
              node.y,
              glowRadius
            );

          glow.addColorStop(
            0,
            `rgba(${node.color},${opacity * 0.3})`
          );

          glow.addColorStop(
            1,
            `rgba(${node.color},0)`
          );

          ctx.beginPath();

          ctx.fillStyle =
            glow;

          ctx.arc(
            node.x,
            node.y,
            glowRadius,
            0,
            Math.PI * 2
          );

          ctx.fill();

          ctx.beginPath();

          ctx.fillStyle =
            `rgba(${node.color},${opacity})`;

          ctx.arc(
            node.x,
            node.y,
            pulseSize,
            0,
            Math.PI * 2
          );

          ctx.fill();
        }
      );

      animId =
        requestAnimationFrame(
          animate
        );
    };

    resize();

    animate();

    window.addEventListener(
      "mousemove",
      onMouseMove
    );

    window.addEventListener(
      "resize",
      resize
    );

    return () => {
      cancelAnimationFrame(
        animId
      );

      window.removeEventListener(
        "mousemove",
        onMouseMove
      );

      window.removeEventListener(
        "resize",
        resize
      );
    };
  }, [isDark]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position:
          "fixed",

        top: 0,
        left: 0,

        width:
          "100%",

        height:
          "100%",

        zIndex: 0,

        pointerEvents:
          "none"
      }}
    />
  );
}
