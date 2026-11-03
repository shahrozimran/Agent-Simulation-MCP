"""Exercise the actual SDK client/server stdio transport, not direct function calls."""
import json
import os
from pathlib import Path
import sys
import socket
import subprocess
import time
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

def test_mcp_stdio_end_to_end():
    async def check():
        server = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).resolve().parents[1]/'mcp_server.py')], env=dict(os.environ))
        with anyio.fail_after(40):
            async with stdio_client(server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    assert len(tools.tools) == 8
                    agents = await session.call_tool('list_agents', {})
                    assert not agents.isError
                    created = await session.call_tool('run_simulation', {'agent_id':'goal_based','scenario_id':'rain_urgent'})
                    assert not created.isError
                    payload = created.structuredContent or json.loads(created.content[0].text)
                    assert payload['metrics']['duration'] == 26.5
                    saved = await session.call_tool('get_run', {'run_id':payload['id']})
                    assert not saved.isError
                    training = await session.call_tool('train_learning', {'episodes':50})
                    assert not training.isError
                    bad = await session.call_tool('run_simulation', {'agent_id':'invalid'})
                    assert bad.isError
                    runs = await session.call_tool('run_comparison', {'seed':99})
                    assert not runs.isError
    anyio.run(check, backend='asyncio')

def test_mcp_http_end_to_end():
    # Separate loopback server against this test's isolated SQLite database.
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve().parents[1]/'mcp_server.py'), '--http', '--port', str(port)], env=dict(os.environ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            assert process.poll() is None, 'HTTP MCP process exited before becoming ready'
            try:
                with socket.create_connection(('127.0.0.1',port),timeout=0.1):
                    break
            except OSError:
                time.sleep(0.05)
        else:
            raise AssertionError('HTTP MCP server did not become ready')
        async def check():
            with anyio.fail_after(20):
                async with streamable_http_client(f'http://127.0.0.1:{port}/mcp') as (read,write,_):
                    async with ClientSession(read,write) as session:
                        await session.initialize()
                        assert len((await session.list_tools()).tools) == 8
                        result = await session.call_tool('run_simulation', {'agent_id':'utility_based'})
                        assert not result.isError
                        payload = result.structuredContent or json.loads(result.content[0].text)
                        assert payload['metrics']['initial_route'] == 'C'
        anyio.run(check,backend='asyncio')
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
