document.addEventListener('DOMContentLoaded', () => {
    VanillaTilt.init(document.querySelectorAll(".animate-3d"), {
        max: 15, // Max tilt rotation (degrees)
        speed: 400, // Speed of the enter/exit transition
        glare: true, // Enable glare effect
        "max-glare": 0.5 // Max glare opacity
    });
});