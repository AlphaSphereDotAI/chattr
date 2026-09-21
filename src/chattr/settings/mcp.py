from agno.tools.mcp import StreamableHTTPClientParams
from pydantic import BaseModel, Field, HttpUrl


class VoiceGeneratorMCPServer(BaseModel, StreamableHTTPClientParams):
    name: str = Field("voice_generator", description="Name of the MCP server instance")
    url: HttpUrl = Field(
        "http://localhost:7861/gradio_api/mcp",
        description="URL of the Voice Generator MCP server instance",
    )


class VideoGeneratorMCPServer(BaseModel, StreamableHTTPClientParams):
    name: str = Field("video_generator", description="Name of the MCP server instance")
    url: HttpUrl = Field(
        "http://localhost:7862/gradio_api/mcp/?tools=generate_video_mcp",
        description="URL of the Video Generator MCP server instance",
    )


class ExtraMCPServer(BaseModel, StreamableHTTPClientParams):
    name: str = Field(..., description="Name of the MCP server instance")
    url: HttpUrl = Field(..., description="URL of the Extra MCP server instance")
