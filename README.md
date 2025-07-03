# 16-Pixels: AI-Powered Pixel Art Generator

Generate 16x16 pixel art from text descriptions using multiple AI image generation services.

## Features

- **Query Classification**: Uses Google Gemini 2.5 Flash to determine if a query is for image generation
- **Multi-Provider Support**: Generates images from multiple AI services simultaneously
- **Pixel Art Conversion**: Automatically converts generated images to authentic 16x16 pixel art
- **Organized Output**: Saves images in timestamped folders organized by provider
- **Docker Support**: Fully containerized for easy deployment

## Supported Image Generation Services

- OpenAI DALL-E
- FreePik
- RunwayML (coming soon)
- KreaAI (coming soon)
- LeonardoAI (coming soon)
- Replicate (coming soon)
- Hugging Face (coming soon)
- Stability AI (coming soon)

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 16-pixels
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t 16-pixels .
```

2. Or use docker-compose:
```bash
docker-compose build
```

## Usage

### Command Line

```bash
# Basic usage
python -m src.main --query "a cute pixel art cat"

# Generate multiple variations
python -m src.main --query "retro game warrior" --variations 4

# Specify output directory
python -m src.main --query "8-bit spaceship" --output-dir ./my-images

# Skip pixel art conversion (keep original resolution)
python -m src.main --query "fantasy castle" --no-pixel-art

# Enable debug logging
python -m src.main --query "pixel art dragon" --debug
```

### Docker

```bash
# Using docker run
docker run --rm \
  -v $(pwd)/output:/app/output \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  16-pixels --query "pixel art mushroom"

# Using docker-compose
docker-compose run --rm app --query "16-bit style robot"
```

## Output Structure

Generated images are saved in timestamped folders:

```
output/
└── 20250328-142536/
    ├── openai/
    │   ├── variation_1.png          # 16x16 pixel art
    │   ├── variation_1_preview.png  # Enlarged preview with grid
    │   └── variation_2.png
    ├── freepik/
    │   └── variation_1.png
    └── metadata.json                # Session information
```

## API Keys Configuration

Create a `.env` file with your API keys:

```env
# Required
GOOGLE_API_KEY=your_google_api_key

# Optional - Add only the services you want to use
OPENAI_API_KEY=your_openai_key
FREEPIK_API_KEY=your_freepik_key
# ... other services
```

## Testing

### Run Integration Tests

```bash
# Local
pytest tests/integration -v

# Docker
docker-compose run --rm test
```

**Note**: Integration tests make real API calls and require valid API keys.

## Development

### Project Structure

```
16-pixels/
├── src/
│   ├── agent/           # Pydantic AI query classifier
│   ├── generators/      # Image generation implementations
│   ├── processors/      # Pixel art processing
│   └── utils/          # Utilities (logging, file management)
├── tests/              # Integration tests
├── output/             # Generated images (git-ignored)
└── requirements.txt    # Python dependencies
```

### Adding New Image Generators

1. Create a new generator class in `src/generators/`
2. Inherit from `ImageGenerator` base class
3. Implement required methods:
   - `generate()`
   - `get_service_name()`
   - `is_available()`
4. Register in `GeneratorRegistry`

## License

[Your License Here]

## Contributing

[Contributing Guidelines]