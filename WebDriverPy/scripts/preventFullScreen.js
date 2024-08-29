document.addEventListener('keydown', function(event) {
    if (event.key === 'F11') {
        event.preventDefault();
        alert('Full-screen mode is disabled!');
    }
});

document.addEventListener('fullscreenchange', function(event) {
    if (document.fullscreenElement) {
        document.exitFullscreen();
        alert('Full-screen mode is disabled!');
    }
});
