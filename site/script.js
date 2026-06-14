/* ======================================================
   EasyHotCorners — Premium Animations & Interactions
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

// ===== Canvas Particle Background (High Performance) =====
const canvas = document.getElementById("canvas-particles");
const ctx = canvas.getContext("2d");

let particles = [];
let mouse = { x: null, y: null, radius: 150 };

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
    }
    update() {
        // Natural drift
        this.x += this.speedX;
        this.y += this.speedY;

        // Bounce/Wrap borders
        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;

        // Push effect from mouse
        if (mouse.x !== null && mouse.y !== null) {
            const dx = mouse.x - this.x;
            const dy = mouse.y - this.y;
            const distance = Math.hypot(dx, dy);
            if (distance < mouse.radius) {
                const force = (mouse.radius - distance) / mouse.radius;
                const forceX = (dx / distance) * force * 1.5;
                const forceY = (dy / distance) * force * 1.5;
                this.x -= forceX;
                this.y -= forceY;
            }
        }
    }
    draw() {
        ctx.fillStyle = "rgba(167, 139, 250, 0.35)";
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fill();
    }
}

function initParticles() {
    particles = [];
    const count = Math.min(80, Math.floor((canvas.width * canvas.height) / 20000));
    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }
}
initParticles();

// Debounce resize particle initialization
let resizeTimeout;
window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(initParticles, 200);
});

// Track mouse position on canvas
window.addEventListener("mousemove", (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});
window.addEventListener("mouseleave", () => {
    mouse.x = null;
    mouse.y = null;
});

// Animation Loop
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();

        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.hypot(dx, dy);

            if (dist < 110) {
                const alpha = (110 - dist) / 110 * 0.12;
                ctx.strokeStyle = `rgba(167, 139, 250, ${alpha})`;
                ctx.lineWidth = 0.6;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// ===== Card spotlight glow (Premium hover effect) =====
document.querySelectorAll(".feature-card").forEach((card) => {
    card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty("--mouse-x", `${x}px`);
        card.style.setProperty("--mouse-y", `${y}px`);
    });
});

// ===== Hide scroll hint on scroll =====
const scrollHint = document.getElementById("scrollHint");
if (scrollHint) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 80) {
            scrollHint.style.opacity = "0";
        } else {
            scrollHint.style.opacity = "";
        }
    }, { passive: true });
}
