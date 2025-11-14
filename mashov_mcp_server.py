#!/usr/bin/env python3
"""
MCP Server for Mashov API
Provides tools to interact with the Mashov school management system
"""

import asyncio
import json
import sys
from typing import Any, Optional, Union, List, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mashov_client import MashovClient
from config import load_config


# Initialize the MCP server
server = Server("mashov-mcp-server")

# Load configuration on startup
load_config()


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="get_all_grades",
            description="Get all grades in graph format, optionally filtered by subject and/or child",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Optional subject name to filter grades"
                    },
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_schools",
            description="Get list of all available schools",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_homework",
            description="Get homework assignments for a child",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_alfon",
            description="Get the class directory (alfon) with classmates' contact information for a child's class",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_behave",
            description="Get behavior events for a child (attendance, absences, good words, homework completion, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_files",
            description="Get files for a child",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_groups",
            description="Get groups/classes the student belongs to",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_timetable",
            description="Get the student's timetable/schedule with lesson times, subjects, and classrooms",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_maakav",
            description="Get maakav (progress tracking) information for the student",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_lessons_history",
            description="Get lessons history for the student with details about topics covered, dates, and teachers",
            inputSchema={
                "type": "object",
                "properties": {
                    "child_guid": {
                        "type": "string",
                        "description": "Optional: Specific child GUID to query"
                    },
                    "child_name": {
                        "type": "string",
                        "description": "Optional: Child's first name to query"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_children",
            description="Get list of all children (for parent accounts). Returns child information including names, GUIDs, classes, and groups. Use this first to find out which children are available, then use child_name or child_guid in other tools.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent]]:
    """Handle tool calls"""
    client = MashovClient.get_instance()
    
    # Check if credentials are configured (authentication will happen automatically on first request)
    if not all([client.username, client.password, client.semel, client.year]):
        return [TextContent(
            type="text",
            text="Error: Not authenticated. Please configure credentials first."
        )]
    
    try:
        if name == "get_all_grades":
            subject = arguments.get("subject")
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_all_grades(subject=subject, child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_schools":
            result = await client.get_schools()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_homework":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_homework(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_alfon":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_alfon(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_behave":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_behave(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_files":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_files(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_groups":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_groups(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_timetable":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_timetable(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_maakav":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_maakav(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_lessons_history":
            child_guid = arguments.get("child_guid")
            child_name = arguments.get("child_name")
            result = await client.get_lessons_history(child_guid=child_guid, child_name=child_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "get_children":
            # Ensure we're logged in first to get the children list
            await client._ensure_authenticated()
            result = client.get_children()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

