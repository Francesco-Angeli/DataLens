particlesJS('particles-js', {
    particles: {
        number: {
            value: 80,
            density: {
                enable: true,
                value_area: 1000
            }
        },
        color: {
            value: '#6d6027'
        },
        shape: {
            type: 'circle'
        },
        opacity: {
            value: 0.3,
            random: false,
            anim: {
                enable: false
            }
        },
        size: {
            value: 4,
            random: true,
            anim: {
                enable: false
            }
        },
        line_linked: {
            enable: true,
            distance: 150,
            color: '#6d6027',
            opacity: 0.2,
            width: 1.5
        },
        move: {
            enable: true,
            speed: 1.5,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false,
            attract: {
                enable: true,
                rotateX: 600,
                rotateY: 1200
            }
        }
    },
    interactivity: {
        detect_on: 'canvas',
        events: {
            onhover: {
                enable: true,
                mode: 'grab'
            },
            onclick: {
                enable: false
            },
            resize: true
        },
        modes: {
            grab: {
                distance: 140,
                line_linked: {
                    opacity: 0.4  
                }
            }
        }
    },
    retina_detect: true
});
