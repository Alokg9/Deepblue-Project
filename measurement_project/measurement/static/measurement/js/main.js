
$(document).ready(function() {
    let measuring = false;
    let calibrating = false;

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    $('#capture-btn').click(function() {
        const mode = $('#measurement-mode').val();
        if (!measuring) {
            measuring = true;
            $(this).addClass('measuring').prop('disabled', true);
            captureAndMeasure(mode);
        }
    });

    $('#calibrate-capture-btn').click(function() {
        const referenceSize = $('#reference-size').val();
        if (!referenceSize) {
            showError('Please enter reference size');
            return;
        }
        if (!calibrating) {
            calibrating = true;
            $(this).prop('disabled', true);
            calibrate(referenceSize);
        }
    });

    $('#measurement-mode').change(function() {
        updateMeasurementGuides($(this).val());
    });
});

function captureAndMeasure(mode) {
    const video = document.getElementById('video-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.width;
    canvas.height = video.height;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    $.ajax({
        url: '/capture_and_measure/',
        type: 'POST',
        data: {
            'image': imageData,
            'mode': mode
        },
        success: function(response) {
            if (response.success) {
                displayMeasurements(response.dimensions, mode);
            } else {
                showError('Measurement failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error: ' + error);
        },
        complete: function() {
            $('#capture-btn').removeClass('measuring').prop('disabled', false);
            measuring = false;
        }
    });
}

function calibrate(referenceSize) {
    const video = document.getElementById('video-feed');
    const canvas = document.createElement('canvas');
    canvas.width = video.width;
    canvas.height = video.height;
    
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    $.ajax({
        url: '/calibrate/',
        type: 'POST',
        data: {
            'image': imageData,
            'reference_size': referenceSize
        },
        success: function(response) {
            if (response.success) {
                showSuccess('Calibration successful!');
                $('#calibrationModal').modal('hide');
            } else {
                showError('Calibration failed: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            showError('Error: ' + error);
        },
        complete: function() {
            $('#calibrate-capture-btn').prop('disabled', false);
            calibrating = false;
        }
    });
}

function displayMeasurements(dimensions, mode) {
    let html = '';
    
    switch(mode) {
        case 'single':
            html = `
                <div class="measurement-result">
                    <div>Width: ${dimensions.width} cm</div>
                    <div>Height: ${dimensions.height} cm</div>
                </div>
            `;
            break;
        case 'multiple':
            html = '<h6>Multiple Objects:</h6>';
            dimensions.forEach((dim, index) => {
                html += `
                    <div class="object-measurement">
                        <div>Object ${index + 1}:</div>
                        <div>Width: ${dim.width} cm</div>
                        <div>Height: ${dim.height} cm</div>
                    </div>
                `;
            });
            break;
        case 'area':
            html = `
                <div class="measurement-result">
                    <div>Area: ${dimensions.area} cm²</div>
                </div>
            `;
            break;
        case 'volume':
            html = `
                <div class="measurement-result">
                    <div>Volume: ${dimensions.volume} cm³</div>
                    <div>Height: ${dimensions.height} cm</div>
                </div>
            `;
            break;
        case 'angle':
            html = `
                <div class="measurement-result">
                    <div>Angle: ${dimensions.angle}°</div>
                </div>
            `;
            break;
    }
    
    $('#measurement-results').html(html);
}

function updateMeasurementGuides(mode) {
    const guides = $('#measurement-guides');
    guides.empty();

    switch(mode) {
        case 'angle':
            guides.append('<div class="guide-line angle-guide"></div>');
            break;
        case 'area':
            guides.append('<div class="guide-box area-guide"></div>');
            break;
        // Add more guide types as needed
    }
}

function showError(message) {
    $('#error-message').text(message);
    new bootstrap.Modal(document.getElementById('errorModal')).show();
}

function showSuccess(message) {
    // You could create a success toast or modal here
    alert(message);
}
