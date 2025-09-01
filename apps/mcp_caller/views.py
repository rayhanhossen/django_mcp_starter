import json
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .mcp_call_tool import call_mcp_tool, MCPError


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

        try:
            data = await call_mcp_tool(
                name="summarize_numbers",
                arguments=payload
            )
            return JsonResponse({"data": data}, status=200)

        except MCPError as me:
            return JsonResponse({"error": str(me)}, status=400)
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

        try:
            data = await call_mcp_tool(
                name="slugify_text",
                arguments=payload
            )
            return JsonResponse({"data": data}, status=200)

        except MCPError as me:
            return JsonResponse({"error": str(me)}, status=400)
        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
