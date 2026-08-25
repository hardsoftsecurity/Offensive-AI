# MCP Practical Lab — Summary & Reference

## 1. Environment Setup

```bash
# Create and activate a virtual environment
python3 -m venv mcp-lab
source mcp-lab/bin/activate

# Install the required package
pip3 install fastmcp
```

---

## 2. MCP Server

The server exposes the three core MCP capabilities — **prompts**, **resources**, and **tools** — using `fastmcp` decorators.

### `server.py`

```python
from fastmcp import FastMCP
from glob import glob

mcp = FastMCP("MCP")

# Prompt — returns a spell-check prompt for a given text
@mcp.prompt()
def spell_check(text: str) -> str:
    """Generates a user message asking for a spell check of an input text."""
    return f"Please check the following text for typos and grammatical errors:\n\n{text}"

# Resource — static URI returning the number of stored files
@mcp.resource("resource://filecount")
def count_files() -> int:
    """Provides the number of stored files."""
    return len(glob("/tmp/*.mcpfile"))

# Resource Template — dynamic URI to retrieve a file's content
@mcp.resource("getfile://{file_name}")
def get_file(file_name: str) -> str:
    """Get content of a stored file."""
    with open(f"/tmp/{file_name}.mcpfile", "r") as f:
        return f.read()

# Tool — stores content to a file on disk
@mcp.tool()
def store_file(file_content: str, file_name: str) -> str:
    """Store a file."""
    with open(f"/tmp/{file_name}.mcpfile", "w+") as f:
        f.write(file_content)
    return file_content

mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

```bash
python3 server.py
```

The server starts on `http://127.0.0.1:8000` using Streamable HTTP transport.

---

## 3. MCP Client

The client connects to the server's `/mcp/` endpoint. All interactions are async.

### 3a. Prompts

```python
import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp/")

async def main():
    async with client:
        prompts = await client.list_prompts()
        result  = await client.get_prompt("spell_check", {"text": "Hello World!"})
        print(result.messages[0].content.text)

asyncio.run(main())
```

| Client Method    | MCP JSON-RPC Method |
| ---------------- | ------------------- |
| `list_prompts()` | `prompts/list`      |
| `get_prompt()`   | `prompts/get`       |

### 3b. Tools

```python
async def main():
    async with client:
        tools  = await client.list_tools()
        result = await client.call_tool("store_file", {
            "file_content": "Hello World!",
            "file_name": "helloworld"
        })
        print(result.content[0].text)
```

| Client Method  | MCP JSON-RPC Method |
| -------------- | ------------------- |
| `list_tools()` | `tools/list`        |
| `call_tool()`  | `tools/call`        |

### 3c. Resources

```python
async def main():
    async with client:
        resources = await client.list_resources()
        count     = await client.read_resource("resource://filecount")
        print(count[0].text)  # "1"

        templates = await client.list_resource_templates()
        content   = await client.read_resource("getfile://helloworld")
        print(content[0].text)  # "Hello World!"
```

| Client Method               | MCP JSON-RPC Method    |
| --------------------------- | ---------------------- |
| `list_resources()`          | `resources/list`       |
| `list_resource_templates()` | `resources/templates/list` |
| `read_resource()`           | `resources/read`       |

---

## 4. Protocol Flow (JSON-RPC 2.0 over HTTP)

### Initialization Phase

1. **Client → Server** — `initialize` request (protocol version, client capabilities, client info).
2. **Server → Client** — `initialize` response (confirmed version, server capabilities: prompts, resources, tools).
3. **Client → Server** — `notifications/initialized` notification.

### Operation Phase

Standard request/response pairs for `prompts/list`, `prompts/get`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, etc.

### Error Handling

If a server-side function throws an exception (e.g., `FileNotFoundError`), `fastmcp` catches it and returns a JSON-RPC error response automatically:

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "error": {
    "code": 0,
    "message": "Error creating resource from template: ... No such file or directory: '/tmp/invalid.mcpfile'"
  }
}
```

---

## 5. Authenticated Connections

Pass custom headers (API keys, Bearer tokens) via the transport config:

```python
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport(
    url="http://localhost:8000/mcp/",
    headers={"X-API-Key": "DummyApiKey1337"}
)
client = Client(transport)
```

---

## 6. Key Takeaways

- `fastmcp` decorators (`@mcp.prompt()`, `@mcp.resource()`, `@mcp.tool()`) auto-derive capability names, descriptions, and parameter schemas from the Python function signature and docstring.
- Transport is **Streamable HTTP** — all messages are JSON-RPC 2.0 payloads inside standard HTTP requests, inspectable with Wireshark.
- Error handling is automatic — unhandled Python exceptions surface as JSON-RPC error responses to the client.
- Resource URIs can be static (`resource://filecount`) or templated (`getfile://{file_name}`).