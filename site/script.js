/* ======================================================
   EasyHotCorners — Animations & Interactions
   ====================================================== */

// ===== Intersection Observer for feature cards =====
const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => {
                    entry.target.classList.add("visible");
                }, delay * 120);
                observer.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.15 }
);

document.querySelectorAll(".feature-card").forEach((card) => {
    observer.observe(card);
});

// ===== Corner glows on mouse proximity =====
const glows = {
    tl: document.querySelector(".corner-glow--tl"),
    tr: document.querySelector(".corner-glow--tr"),
    bl: document.querySelector(".corner-glow--bl"),
    br: document.querySelector(".corner-glow--br"),
};

const THRESHOLD = 250; // px from corner to start glow

document.addEventListener("mousemove", (e) => {
    const x = e.clientX;
    const y = e.clientY;
    const w = window.innerWidth;
    const h = window.innerHeight;

    const distTL = Math.hypot(x, y);
    const distTR = Math.hypot(w - x, y);
    const distBL = Math.hypot(x, h - y);
    const distBR = Math.hypot(w - x, h - y);

    glows.tl.classList.toggle("active", distTL < THRESHOLD);
    glows.tr.classList.toggle("active", distTR < THRESHOLD);
    glows.bl.classList.toggle("active", distBL < THRESHOLD);
    glows.br.classList.toggle("active", distBR < THRESHOLD);
});

// ===== Floating particles in hero =====
const particleContainer = document.getElementById("particles");

function createParticle() {
    const el = document.createElement("div");
    const size = Math.random() * 3 + 1;
    el.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: rgba(167, 139, 250, ${Math.random() * 0.3 + 0.1});
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: particleDrift ${Math.random() * 10 + 10}s linear infinite;
        pointer-events: none;
    `;
    particleContainer.appendChild(el);
}

// Generate particles
for (let i = 0; i < 40; i++) createParticle();

// Inject the particle drift keyframes
const style = document.createElement("style");
style.textContent = `
    @keyframes particleDrift {
        0%   { transform: translate(0, 0) scale(1);   opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translate(${Math.random() > 0.5 ? '' : '-'}60px, -120px) scale(0.5); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ===== Hide scroll hint on scroll =====
const scrollHint = document.getElementById("scrollHint");
window.addEventListener("scroll", () => {
    if (window.scrollY > 80) {
        scrollHint.style.opacity = "0";
    } else {
        scrollHint.style.opacity = "";
    }
}, { passive: true });
