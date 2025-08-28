import asyncio
import json
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fastmcp import Client

@csrf_exempt
async def summarize_numbers_views(request: HttpRequest) -> JsonResponse | None:
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
        if not isinstance(payload, dict):
            return JsonResponse({"error": "Payload must be a JSON object"}, status=400)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # mcp client
    client = Client("http://localhost:9000/mcp")

    try:
        async with client:
            await client.ping() # quick health check of client
            result = await asyncio.wait_for(client.call_tool(name="summarize_numbers", arguments=payload), timeout=10.0)
            data = result.data
            if isinstance(data, dict) and data.get("response") is False:
                return JsonResponse({"error": data.get("error")}, status=400)
            return JsonResponse({"data": data}, status=200)
    except asyncio.TimeoutError:
        return JsonResponse({"error": "Server timed out"}, status=500)
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=500)

@csrf_exempt
async def slugify_text_views(request: HttpRequest) -> JsonResponse | None:
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
        if not isinstance(payload, dict):
            return JsonResponse({"error": "Payload must be a JSON object"}, status=400)
    except json.decoder.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # mcp client
    client = Client("http://localhost:9000/mcp")

    try:
        async with client:
            await client.ping() # quick health check of client
            result = await asyncio.wait_for(client.call_tool(name="slugify_text", arguments=payload), timeout=10.0)
            data = result.data
            if isinstance(data, dict) and data.get("response") is False:
                return JsonResponse({"error": data.get("error")}, status=400)
            return JsonResponse({"data": data}, status=200)
    except asyncio.TimeoutError:
        return JsonResponse({"error": "Server timed out"}, status=500)
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=500)