#!/usr/bin/env python3
"""
Simple MCP client example with OAuth authentication support.

- Connects to an MCP server using Streamable HTTP or SSE transport with OAuth.
- Starts a local HTTP callback server for the OAuth redirect.
- Provides a minimal interactive REPL to list and call tools.

Usage:
  # Env-based (defaults shown)
  # Windows PowerShell:
  #   $env:SERVER_URL="http://localhost:8000/mcp"
  #   $env:TRANSPORT="streamable_http"
  #   python main.py
  #
  # CLI-based overrides:
  #   python main.py --server-url http://localhost:8000/mcp --transport streamable_http
"""

import asyncio
import json
import os
import sys
import threading
import time
import webbrowser
import argparse
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken


class InMemoryTokenStorage(TokenStorage):
    """Simple in-memory token storage implementation."""

    def __init__(self):
        self._tokens: Optional[OAuthToken] = None
        self._client_info: Optional[OAuthClientInformationFull] = None

    async def get_tokens(self) -> Optional[OAuthToken]:
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens

    async def get_client_info(self) -> Optional[OAuthClientInformationFull]:
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info


class CallbackHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler to capture OAuth callback."""

    def __init__(self, request, client_address, server, callback_data):
        """Initialize with callback data storage."""
        self.callback_data = callback_data
        super().__init__(request, client_address, server)

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        if "code" in query_params:
            self.callback_data["authorization_code"] = query_params["code"][0]
            self.callback_data["state"] = query_params.get("state", [None])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body>
                <h2>Authorization received.</h2>
                <p>You can close this window and return to the terminal.</p>
                </body></html>
            """)
        elif "error" in query_params:
            self.callback_data["error"] = query_params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
                <html><body>
                <h2>Error: {query_params["error"]}</h2>
                <p>You can close this window and return to the terminal.</p>
                </body></html>
            """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class CallbackServer:
    """Simple server to handle OAuth callbacks."""

    def __init__(self, port=3030):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.callback_data = {"authorization_code": None, "state": None, "error": None}

    def _create_handler_with_data(self):
        """Create a handler class with access to callback data."""
        callback_data = self.callback_data

        class DataCallbackHandler(CallbackHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server, callback_data)

        return DataCallbackHandler

    def start(self):
        """Start the callback server in a background thread."""
        handler_class = self._create_handler_with_data()
        self.server = HTTPServer(("localhost", self.port), handler_class)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"🖥️ Started callback server on http://localhost:{self.port}")

    def stop(self):
        """Stop the callback server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)

    def wait_for_callback(self, timeout=300):
        """Wait for OAuth callback with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.callback_data["authorization_code"]:
                return self.callback_data["authorization_code"]
            elif self.callback_data["error"]:
                raise Exception(f"OAuth error: {self.callback_data['error']}")
            time.sleep(0.1)
        raise Exception("Timeout waiting for OAuth callback")

    def get_state(self):
        """Get the received state parameter."""
        return self.callback_data["state"]


class SimpleAuthClient:
    """Simple MCP client with auth support."""

    def __init__(self, server_url: str, transport_type: str = "streamable_http"):
        self.server_url = server_url
        self.transport_type = transport_type
        self.session: Optional[ClientSession] = None

    async def connect(self):
        """Connect to the MCP server."""
        print(f"🔗 Attempting to connect to {self.server_url}...")
        try:
            callback_server = CallbackServer(port=3030)
            callback_server.start()

            async def callback_handler() -> tuple[str, Optional[str]]:
                """Wait for OAuth callback and return auth code and state."""
                print("⏳ Waiting for authorization callback...")
                try:
                    auth_code = callback_server.wait_for_callback(timeout=300)
                    return auth_code, callback_server.get_state()
                finally:
                    callback_server.stop()

            client_metadata_dict = {
                "client_name": "Simple Auth Client",
                "redirect_uris": ["http://localhost:3030/callback"],
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "client_secret_post",
            }

            async def _default_redirect_handler(authorization_url: str) -> None:
                """Default redirect handler that opens the URL in a browser."""
                print(f"Opening browser for authorization: {authorization_url}")
                webbrowser.open(authorization_url)

            # Create OAuth authentication handler
            oauth_auth = OAuthClientProvider(
                server_url=self.server_url.replace("/mcp", ""),
                client_metadata=OAuthClientMetadata.model_validate(client_metadata_dict),
                storage=InMemoryTokenStorage(),
                redirect_handler=_default_redirect_handler,
                callback_handler=callback_handler,
            )

            # Create transport with auth handler based on transport type
            if self.transport_type == "sse":
                print("📡 Opening SSE transport connection with auth...")
                async with sse_client(
                    url=self.server_url,
                    auth=oauth_auth,
                    timeout=60,
                ) as (read_stream, write_stream):
                    await self._run_session(read_stream, write_stream, None)
            else:
                print("📡 Opening StreamableHTTP transport connection with auth...")
                async with streamablehttp_client(
                    url=self.server_url,
                    auth=oauth_auth,
                    timeout=timedelta(seconds=60),
                ) as (read_stream, write_stream, get_session_id):
                    await self._run_session(read_stream, write_stream, get_session_id)

        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            import traceback
            traceback.print_exc()

    async def _run_session(self, read_stream, write_stream, get_session_id):
        """Run the MCP session with the given streams."""
        print("🤝 Initializing MCP session...")
        async with ClientSession(read_stream, write_stream) as session:
            self.session = session
            print("⚡ Starting session initialization...")
            await session.initialize()
            print("✨ Session initialization complete!")

            print(f"\n✅ Connected to MCP server at {self.server_url}")
            if get_session_id:
                session_id = get_session_id()
                if session_id:
                    print(f"Session ID: {session_id}")

            # Run interactive loop
            await self.interactive_loop()

    async def list_tools(self):
        """List available tools from the server."""
        if not self.session:
            print("❌ Not connected to server")
            return
        try:
            result = await self.session.list_tools()
            if hasattr(result, "tools") and result.tools:
                print("\n📋 Available tools:")
                for i, tool in enumerate(result.tools, 1):
                    print(f"{i}. {tool.name}")
                    if tool.description:
                        print(f"   Description: {tool.description}")
                print()
            else:
                print("No tools available")
        except Exception as e:
            print(f"❌ Failed to list tools: {e}")

    async def call_tool(self, tool_name: str, arguments: Optional[dict[str, Any]] = None):
        """Call a specific tool."""
        if not self.session:
            print("❌ Not connected to server")
            return
        try:
            result = await self.session.call_tool(tool_name, arguments or {})
            print(f"\n🔧 Tool '{tool_name}' result:")
            if hasattr(result, "content"):
                for content in result.content:
                    if getattr(content, "type", None) == "text":
                        print(content.text)
                    else:
                        print(content)
            else:
                print(result)
        except Exception as e:
            print(f"❌ Failed to call tool '{tool_name}': {e}")

    async def interactive_loop(self):
        """Run interactive command loop."""
        print("\n🎯 Interactive MCP Client")
        print("Commands:")
        print("  list")
        print("  call <tool_name> <json-args>")
        print("  quit")
        print()

        loop = asyncio.get_event_loop()
        while True:
            try:
                user_input = await loop.run_in_executor(None, lambda: input("mcp> ").strip())
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Exiting.")
                return

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("👋 Bye.")
                return

            if user_input.lower() == "list":
                await self.list_tools()
                continue

            if user_input.lower().startswith("call "):
                parts = user_input.split(" ", 2)
                if len(parts) < 2:
                    print("Usage: call <tool_name> <json-args>")
                    continue

                tool_name = parts[1]
                args_obj: dict[str, Any] = {}
                if len(parts) == 3 and parts[1].strip():
                    try:
                        args_obj = json.loads(parts[1])
                    except json.JSONDecodeError as je:
                        print(f"❌ Invalid JSON args: {je}")
                        continue

                await self.call_tool(tool_name, args_obj)
                continue

            print("Unknown command. Try: list | call <tool> <json-args> | quit")


def parse_args():
    parser = argparse.ArgumentParser(description="Simple MCP OAuth client")
    parser.add_argument("--server-url", default=os.getenv("SERVER_URL", "http://localhost:8000/mcp"),
                        help="MCP server URL (default from SERVER_URL env or http://localhost:8000/mcp)")
    parser.add_argument("--transport", choices=["streamable_http", "sse"],
                        default=os.getenv("TRANSPORT", "streamable_http"),
                        help="Transport type (default from TRANSPORT env or streamable_http)")
    return parser.parse_args()


async def amain():
    args = parse_args()
    client = SimpleAuthClient(server_url=args.server_url, transport_type=args.transport)
    await client.connect()


def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")


if __name__ == "__main__":
    main()
