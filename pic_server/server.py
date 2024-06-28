from flask import Flask, send_file, jsonify, render_template_string, request
from picamera2 import Picamera2
import time
import os

app = Flask(__name__)
picam2 = Picamera2()

# Ensure the static directory exists
os.makedirs('static', exist_ok=True)

captured_images = []

@app.route('/')
def index():
    return render_template_string('''
        <h1>Raspberry Pi Camera</h1>
        <form id="capture-form">
            <label for="resolution">Select Resolution:</label>
            <select name="resolution" id="resolution">
                <option value="640x480">640x480</option>
                <option value="1280x720">1280x720</option>
                <option value="1920x1080">1920x1080</option>
                <option value="4056x3040">12MP (4056x3040)</option>
            </select>
            <button type="submit">Capture Image</button>
        </form>
        <br>
        <div id="result"></div>
        <h2>Captured Images</h2>
        <ul id="image-list">
            {% for image in images %}
                <li>
                    <a href="{{ image['view'] }}">View</a> |
                    <a href="{{ image['download'] }}">Download</a>
                </li>
            {% endfor %}
        </ul>
        <script>
            document.getElementById('capture-form').addEventListener('submit', function(event) {
                event.preventDefault();
                var formData = new FormData(event.target);
                fetch('/api/capture', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        document.getElementById('result').innerText = data.message;
                        updateImageList();
                    } else if (data.error) {
                        document.getElementById('result').innerText = data.error;
                    }
                })
                .catch(error => {
                    document.getElementById('result').innerText = 'An error occurred: ' + error;
                });
            });

            function updateImageList() {
                fetch('/api/images')
                .then(response => response.json())
                .then(data => {
                    const imageList = document.getElementById('image-list');
                    imageList.innerHTML = '';
                    data.images.forEach(image => {
                        const listItem = document.createElement('li');
                        const viewLink = document.createElement('a');
                        viewLink.href = image.view;
                        viewLink.innerText = 'View';
                        const downloadLink = document.createElement('a');
                        downloadLink.href = image.download;
                        downloadLink.innerText = 'Download';
                        listItem.appendChild(viewLink);
                        listItem.innerHTML += ' | ';
                        listItem.appendChild(downloadLink);
                        imageList.appendChild(listItem);
                    });
                });
            }

            document.addEventListener('DOMContentLoaded', function() {
                updateImageList();
            });
        </script>
    ''', images=captured_images)


@app.route('/api/capture', methods=['POST'])
def api_capture():
    try:
        resolution = request.form.get('resolution')
        width, height = map(int, resolution.split('x'))
        config = picam2.create_still_configuration(main={"size": (width, height)})
        picam2.configure(config)

        picam2.start()
        time.sleep(2)
        timestamp = int(time.time())
        image_filename = f"image_{timestamp}.jpg"
        image_path = os.path.join("static", image_filename)
        picam2.capture_file(image_path)
        picam2.stop()

        captured_images.append({
            "view": f"/static/{image_filename}",
            "download": f"/api/download/{image_filename}"
        })

        return jsonify({"message": "Image captured successfully!", "path": image_path})
    except Exception as e:
        picam2.stop()  # Ensure the camera is stopped on error
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>')
def api_download(filename):
    image_path = os.path.join("static", filename)
    if os.path.exists(image_path):
        return send_file(image_path, as_attachment=True)
    else:
        return jsonify({"error": "No image captured yet."}), 404


@app.route('/api/images')
def api_images():
    return jsonify({"images": captured_images})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

