import asyncio
import json
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from fastmcp import Client

@method_decorator(csrf_exempt, name="dispatch")
class SummarizeNumbersView(View):
    # Only allow POST; other methods will automatically return 405
    http_method_names = ["post"]

    async def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # Parse JSON body
        try:
            payload_raw = request.body or b"{}"
            payload = json.loads(payload_raw.decode("utf-8"))
            if not isinstance(payload, dict):
                return JsonResponse({"error": "Payload must be a JSON object"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        client = Client("http://localhost:9000/mcp")

        try:
            async with client:
                # quick health check
                await client.ping()
                # call MCP tool (with timeout)
                result = await asyncio.wait_for(
                    client.call_tool(name="summarize_numbers", arguments=payload),
                    timeout=10.0,
                )
                data = getattr(result, "data", result)
                if isinstance(data, dict) and data.get("response") is False:
                    return JsonResponse({"error": data.get("error")}, status=400)
                return JsonResponse({"data": data}, status=200)

        except asyncio.TimeoutError:
            return JsonResponse({"error": "Server timed out"}, status=500)
        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class SlugifyTextView(View):
    http_method_names = ["post"]

    async def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # Parse JSON payload
        try:
            payload_raw = request.body or b"{}"
            payload = json.loads(payload_raw.decode("utf-8"))
            if not isinstance(payload, dict):
                return JsonResponse({"error": "Payload must be a JSON object"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        client = Client("http://localhost:9000/mcp")

        try:
            async with client:
                # quick health check
                await client.ping()
                # call MCP tool with timeout
                result = await asyncio.wait_for(
                    client.call_tool(name="slugify_text", arguments=payload),
                    timeout=10.0,
                )
                data = getattr(result, "data", result)

                if isinstance(data, dict) and data.get("response") is False:
                    return JsonResponse({"error": data.get("error")}, status=400)

                return JsonResponse({"data": data}, status=200)

        except asyncio.TimeoutError:
            return JsonResponse({"error": "Server timed out"}, status=500)
        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)