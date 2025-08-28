# Django MCP Starter

A starter Django project that demonstrates how to **call Model Context Protocol (MCP) tools** directly from Django views using [`fastmcp`](https://pypi.org/project/fastmcp/).

This project is designed to:
- Provide a **minimal working example** of integrating an MCP client inside Django.
- Show how to call fixed tools (e.g., `summarize_numbers`, `slugify_text`) from a Django endpoint.
- Work with **Streamable HTTP** MCP transports.

---

## 🚀 Requirements
- Python 3.11+
- social-auth-core==4.7.0
- social-auth-app-django==5.5.1
- fastmcp==2.11.3
- Django==5.2.5

---

## 📦 Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/django_mcp_starter.git
cd django_mcp_starter

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
---

## ▶️ Running the MCP Server
```bash
  # locate to server directory
  cd mcp_server
  
  # Run the mcp server 
  python server.py
```

---
## ▶️ Running Django
### In a separate terminal:
```bash
  # Make Migrations 
  python manage.py makemigrations 
  
  # Migrate 
  python manage.py migrate 
  
  # Run the server 
  python manage.py runserver

```
### Django will start on http://127.0.0.1:8000

---
## 📡 Endpoints
### 1. Summarize Numbers

- URL: POST /api/summarize-numbers
- Description: Calls the summarize_numbers tool from the MCP server.
- Request Body (JSON):
```json
    {
      "numbers": [2.5, 7, 3.5, 7, 9.25]
    }
 
```
- Example response 
```json
    {
        "data": {
            "response": true,
            "data": {
                "count": 5,
                "total": 29.25,
                "mean": 5.85,
                "minimum": 2.5,
                "maximum": 9.25
            }
        }
    }

```

### 2. Slugify text

- URL: POST /api/slugify-text
- Description: Calls the slugify_text tool from the MCP server.
- Request Body (JSON):
```json
    {
      "text":"Hello, Django + MCP!"
    }
 
```
- Example response 
```json
    {
        "data": {
            "response": true,
            "data": {
                "slug": "hello-django-mcp",
                "original_length": 20,
                "truncated_flag": false
            }
        }
    }

```