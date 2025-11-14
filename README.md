# Mashov MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

An MCP (Model Context Protocol) server for interacting with the Mashov school management system API.

## Features

- 📊 Get average of all grades
- 📈 Get all grades in graph format (optionally filtered by subject)
- 🎓 Get average of Bagrut (matriculation) grades
- 🏫 Get list of all schools
- 📸 Get user's profile picture
- 👥 Get user's class list
- 💬 Get messages
- 📅 Get schedule/timetable

## Prerequisites

**Choose one of the following:**

### Option 1: Docker (Recommended for Easy Setup) 🐳
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Mashov account credentials

### Option 2: Python (For Development)
- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Mashov account credentials

## Installation

### 🐳 Option 1: Using Docker (Recommended)

1. **Clone this repository**:
```bash
git clone https://github.com/AmitMarcus/MashovMCP.git
cd MashovMCP
```

2. **Build the Docker image** (required before using with MCP):
```bash
docker build -t mashov-mcp-server:latest .
```

⚠️ **Important**: You must build the image before configuring your MCP client.

3. **Verify the image was built**:
```bash
docker images | grep mashov-mcp-server
```

You should see:
```
mashov-mcp-server   latest   ...   ...   ...
```

4. **Test it (optional)**:
```bash
docker run -i --rm \
  -e MASHOV_USERNAME="your_username" \
  -e MASHOV_PASSWORD="your_password" \
  -e MASHOV_SEMEL="your_school_id" \
  -e MASHOV_YEAR="2025" \
  mashov-mcp-server:latest
```

### 🐍 Option 2: Using Python + uv

1. **Clone this repository**:
```bash
git clone https://github.com/AmitMarcus/MashovMCP.git
cd MashovMCP
```

2. **Install uv** (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **Install dependencies**:
```bash
uv pip install -e .
```

4. **Configure credentials**:
```bash
cp env.example .env
# Edit .env with your Mashov credentials
```


## Configuration

Create a `.env` file with your Mashov credentials:

```env
MASHOV_USERNAME=your_username
MASHOV_PASSWORD=your_password
MASHOV_SEMEL=your_school_id
MASHOV_YEAR=2024
```

## Usage

### Testing the API (Without MCP)

Before using the MCP server, you can test the API client directly:

```bash
python test_api.py
```

This script will:
- Test authentication
- Test API endpoints
- Show detailed results
- Help debug API issues

This is useful for:
- Verifying your credentials work
- Debugging API endpoint issues
- Understanding the API response format
- Testing before integrating with MCP

### Running the MCP Server

The server runs via stdio and communicates using the MCP protocol:

```bash
python mashov_mcp_server.py
```

### MCP Client Configuration

To use this server with an MCP client (like Claude Desktop), add it to your MCP configuration file.

#### Option 1: Using Docker 🐳 (Recommended)

```json
{
  "mcpServers": {
    "mashov": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "MASHOV_USERNAME=your_username",
        "-e", "MASHOV_PASSWORD=your_password",
        "-e", "MASHOV_SEMEL=your_school_id",
        "-e", "MASHOV_YEAR=2025",
        "mashov-mcp-server:latest"
      ]
    }
  }
}
```

#### Option 2: Using Python 🐍

```json
{
  "mcpServers": {
    "mashov": {
      "command": "python",
      "args": ["/absolute/path/to/MashovMCP/mashov_mcp_server.py"],
      "env": {
        "MASHOV_USERNAME": "your_username",
        "MASHOV_PASSWORD": "your_password",
        "MASHOV_SEMEL": "your_school_id",
        "MASHOV_YEAR": "2025"
      }
    }
  }
}
```

## Available Tools

### `get_grades_average`
Get the average of all grades for the authenticated user.

### `get_all_grades`
Get all grades in graph format, optionally filtered by subject.
- Parameters:
  - `subject` (optional): Subject name to filter grades

### `get_bagrut_average`
Get the average of all Bagrut (matriculation) grades.

### `get_schools`
Get list of all available schools.

### `get_user_picture`
Get the authenticated user's profile picture.

### `get_class_list`
Get the user's class list.

### `get_messages`
Get messages for the authenticated user.
- Parameters:
  - `limit` (optional): Maximum number of messages to retrieve (default: 10)

### `get_schedule`
Get the user's schedule/timetable.

## Project Structure

```
MashovMCP/
├── mashov_mcp_server.py      # Main MCP server implementation
├── mashov_client.py          # Mashov API client wrapper
├── config.py                 # Configuration handling
├── pyproject.toml            # Project metadata and dependencies (uv/pip)
├── Dockerfile                # Docker image definition
├── .dockerignore             # Docker build exclusions
├── test_api.py               # API test script
├── .gitignore                # Git ignore rules
├── env.example               # Example environment configuration
├── AUTHENTICATION.md         # Authentication flow documentation
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
