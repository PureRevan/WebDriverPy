async function startRecording() {
    const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
            mediaSource: 'screen',
            cursor: 'never',
            width: { ideal: !__::RES_WIDTH_TEMPLATE_DUMMY::__! },
            height: { ideal: !__::RES_HEIGHT_TEMPLATE_DUMMY::__! },
            frameRate: { ideal: !__::FPS_IDEAL_TEMPLATE_DUMMY::__!, max: !__::FPS_MAX_TEMPLATE_DUMMY::__! }
        }
    });

    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorder.ondataavailable = function(event) {
        if (event.data.size > 0) {
            chunks.push(event.data);
        }
    };

    mediaRecorder.onstop = function() {
        const blob = new Blob(chunks, { type: chunks[0].type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '!__::NAME_TEMPLATE_DUMMY::__!';
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
    };

    mediaRecorder.start();

    const duration = !__::DURATION_TEMPLATE_DUMMY::__!;
    const startTime = performance.now();

    function checkRecordingDuration() {
        const elapsedTime = performance.now() - startTime;
        if (elapsedTime >= duration + !__::BUFFER_MS_TEMPLATE_DUMMY::__!) {
            mediaRecorder.stop();
        } else {
            requestAnimationFrame(checkRecordingDuration);
        }
    }

    requestAnimationFrame(checkRecordingDuration);
}

startRecording();
