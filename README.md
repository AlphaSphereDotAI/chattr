---
title: Chattr
emoji: 💬
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
short_description: Chat with Characters
---

# **Chattr**: App part of the Chatacter Backend

## Environment Variables

The configuration of the server is done using environment variables:

| Name                       | Description                | Default Value                              |
|----------------------------|----------------------------|:-------------------------------------------|
| `MODEL__URL`               | OpenAI‑compatible endpoint | `https://api.groq.com/openai/v1`           |
| `MODEL__NAME`              |                            | `llama3-70b-8192`                          |
| `MODEL__API_KEY`           |                            | `None`                                     |
| `MODEL__TEMPERATURE`       |                            | `0.0`                                      |
| `SHORT_TERM_MEMORY__URL`   |                            | `redis://localhost:6379`                   |
| `VECTOR_DATABASE__NAME`    |                            | `chattr`                                   |
| `VOICE_GENERATOR_MCP__URL` |                            | `http://localhost:8001/gradio_api/mcp/sse` |
| `VIDEO_GENERATOR_MCP__URL` |                            | `http://localhost:8002/gradio_api/mcp/sse` |
| `DIRECTORY__ASSETS`        |                            | `./assets`                                 |
| `DIRECTORY__LOG`           |                            | `./logs`                                   |
| `DIRECTORY__IMAGE`         |                            | `./assets/image`                           |
| `DIRECTORY__AUDIO`         |                            | `./assets/audio`                           |
| `DIRECTORY__VIDEO`         |                            | `./assets/video`                           |