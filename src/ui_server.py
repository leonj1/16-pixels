#!/usr/bin/env python3
import os
import json
import mimetypes
from pathlib import Path
from flask import Flask, render_template_string, send_file, abort

app = Flask(__name__)

OUTPUT_DIR = "/app/output"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>16-Pixels Output Browser</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .file-item { margin: 5px 0; }
        .folder-icon { color: #ffc107; }
        .file-icon { color: #6c757d; }
        .image-preview { max-width: 100%; height: auto; margin: 20px 0; }
        .json-content { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .breadcrumb-item a { text-decoration: none; }
    </style>
</head>
<body>
    <div class="container mt-4">
        <h1 class="mb-4">16-Pixels Output Browser</h1>
        
        <!-- Breadcrumb Navigation -->
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Output</a></li>
                {% for part in breadcrumb %}
                <li class="breadcrumb-item {% if loop.last %}active{% endif %}">
                    {% if loop.last %}
                        {{ part.name }}
                    {% else %}
                        <a href="{{ part.url }}">{{ part.name }}</a>
                    {% endif %}
                </li>
                {% endfor %}
            </ol>
        </nav>

        <!-- Content -->
        {% if is_file %}
            {% if is_image %}
                <div class="text-center">
                    <img src="{{ file_url }}" class="image-preview" alt="{{ filename }}">
                </div>
            {% elif is_json %}
                <h3>{{ filename }}</h3>
                <div class="json-content">
                    <pre>{{ json_content }}</pre>
                </div>
            {% else %}
                <h3>{{ filename }}</h3>
                <p>File type: {{ mime_type }}</p>
                <a href="{{ file_url }}" class="btn btn-primary" download>Download File</a>
            {% endif %}
        {% else %}
            <!-- Directory Listing -->
            <div class="list-group">
                {% if path != '/' %}
                <a href="{{ parent_url }}" class="list-group-item list-group-item-action">
                    <i class="bi bi-arrow-left"></i> ..
                </a>
                {% endif %}
                
                {% for item in items %}
                <a href="{{ item.url }}" class="list-group-item list-group-item-action">
                    {% if item.is_dir %}
                        <i class="bi bi-folder-fill folder-icon"></i> {{ item.name }}/
                    {% else %}
                        <i class="bi bi-file-earmark file-icon"></i> {{ item.name }}
                        {% if item.size %}
                            <small class="text-muted">({{ item.size }})</small>
                        {% endif %}
                    {% endif %}
                </a>
                {% endfor %}
            </div>
            
            {% if not items and path == '/' %}
            <div class="alert alert-info mt-3">
                No output files found. Run the image generator to create some content!
            </div>
            {% endif %}
        {% endif %}
    </div>
    
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
</body>
</html>
"""

def get_breadcrumb(path):
    """Generate breadcrumb navigation data"""
    if path == '/':
        return []
    
    parts = path.strip('/').split('/')
    breadcrumb = []
    current_path = ''
    
    for part in parts:
        current_path += '/' + part
        breadcrumb.append({
            'name': part,
            'url': current_path
        })
    
    return breadcrumb

def format_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

@app.route('/')
@app.route('/<path:filepath>')
def browse(filepath=''):
    """Browse files and directories"""
    # Normalize path
    if filepath:
        filepath = filepath.strip('/')
    
    full_path = os.path.join(OUTPUT_DIR, filepath)
    
    # Security check - ensure we're within OUTPUT_DIR
    try:
        full_path = os.path.realpath(full_path)
        if not full_path.startswith(os.path.realpath(OUTPUT_DIR)):
            abort(403)
    except:
        abort(404)
    
    if not os.path.exists(full_path):
        abort(404)
    
    # Handle file display
    if os.path.isfile(full_path):
        mime_type, _ = mimetypes.guess_type(full_path)
        is_image = mime_type and mime_type.startswith('image/')
        is_json = full_path.endswith('.json')
        
        context = {
            'is_file': True,
            'filename': os.path.basename(full_path),
            'file_url': f'/raw/{filepath}',
            'path': f'/{filepath}',
            'breadcrumb': get_breadcrumb(filepath),
            'is_image': is_image,
            'is_json': is_json,
            'mime_type': mime_type or 'unknown'
        }
        
        if is_json:
            try:
                with open(full_path, 'r') as f:
                    json_data = json.load(f)
                    context['json_content'] = json.dumps(json_data, indent=2)
            except:
                context['json_content'] = 'Error reading JSON file'
        
        return render_template_string(HTML_TEMPLATE, **context)
    
    # Handle directory listing
    items = []
    try:
        for item in sorted(os.listdir(full_path)):
            if item.startswith('.'):
                continue
                
            item_path = os.path.join(full_path, item)
            item_url = f'/{filepath}/{item}' if filepath else f'/{item}'
            
            item_data = {
                'name': item,
                'url': item_url,
                'is_dir': os.path.isdir(item_path)
            }
            
            if os.path.isfile(item_path):
                try:
                    size = os.path.getsize(item_path)
                    item_data['size'] = format_size(size)
                except:
                    pass
            
            items.append(item_data)
    except:
        abort(500)
    
    # Sort directories first, then files
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    parent_url = '/' + '/'.join(filepath.split('/')[:-1]) if filepath else '/'
    
    context = {
        'is_file': False,
        'items': items,
        'path': f'/{filepath}' if filepath else '/',
        'parent_url': parent_url,
        'breadcrumb': get_breadcrumb(filepath)
    }
    
    return render_template_string(HTML_TEMPLATE, **context)

@app.route('/raw/<path:filepath>')
def serve_file(filepath):
    """Serve raw file content"""
    full_path = os.path.join(OUTPUT_DIR, filepath)
    
    # Security check
    try:
        full_path = os.path.realpath(full_path)
        if not full_path.startswith(os.path.realpath(OUTPUT_DIR)):
            abort(403)
    except:
        abort(404)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        abort(404)
    
    return send_file(full_path)

if __name__ == '__main__':
    port = int(os.environ.get('UI_PORT', 8080))
    print(f"Starting 16-Pixels UI server on port {port}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Check if output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
    
    app.run(host='0.0.0.0', port=port, debug=False)