# 16-Pixels

Generate 16x16 pixel art from text descriptions using AI image services.

## Requirements

Create a `.env` file with your API keys:

```env
# Required
GOOGLE_API_KEY=your_google_api_key

# Optional (add services you want to use)
OPENAI_API_KEY=your_openai_key
FREEPIK_API_KEY=your_freepik_key
```

## Build

```bash
make build
```

## Generate Images

Generate pixel art with your text description:

```bash
make run QUERY="a cute pixel art cat"
```

Specify the number of variations (default is 1):

```bash
make run QUERY="retro game warrior" VARIATIONS=4
```

## View Output

Start the web UI to browse generated images:

```bash
make build-ui
make start-ui
```

Access the UI at http://localhost:8080

To use a different port:

```bash
make start-ui UI_PORT=8090
```

Stop the UI:

```bash
make stop-ui
```