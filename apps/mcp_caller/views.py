import json
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .mcp_call_tool import call_mcp_tool, MCPError
from .services.intent_router import parse_intent
from .services.llama_summary_local import summarize_with_llama_local


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


@method_decorator(csrf_exempt, name="dispatch")
class ChatToolView(View):
    http_method_names = ["post"]

    async def post(self, request: HttpRequest, *args, **kwargs):
        # 1) Parse input
        try:
            payload_raw = request.body or b"{}"
            try:
                body = json.loads(payload_raw.decode("utf-8"))
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON")
            if not isinstance(body, dict):
                raise ValueError("Payload must be a JSON object")
            message = (body.get("message") or "").strip()
            if not message:
                return JsonResponse({"error": "message is required"}, status=400)
        except ValueError as ve:
            return JsonResponse({"error": str(ve)}, status=400)

        # --- Single helper for Llama SSE streaming ---
        async def llama_event_stream(text: str):
            try:
                async for chunk in summarize_with_llama_local(text):
                    yield f"data: {chunk}\n\n"
                yield "event: done\ndata: [DONE]\n\n"
            except Exception as e:
                err = str(e).replace("\n", " ")
                yield f"event: error\ndata: {json.dumps({'error': err})}\n\n"
                yield "event: done\ndata: [DONE]\n\n"

        # 2) Intent → tool + args
        try:
            tool_name, arguments = await parse_intent(message)
        except Exception:
            tool_name, arguments = None, None

        # Fallback A: no tool detected → stream Llama on the user's message
        if not tool_name:
            return StreamingHttpResponse(
                llama_event_stream(message),
                content_type="text/event-stream"
            )

        # If tool found → print it
        print("Tool found:", tool_name)

        # 3) Run tool
        try:
            tool_data = await call_mcp_tool(
                name=tool_name,
                arguments=arguments,
                timeout=12.0,
            )
        except MCPError as me:
            # Fallback B: tool missing → stream Llama on the user's message
            lower_msg = str(me).lower()
            if "not found" in lower_msg or "unknown tool" in lower_msg or "toolnotfound" in lower_msg:
                return StreamingHttpResponse(
                    llama_event_stream(message),
                    content_type="text/event-stream"
                )
            # Other MCP errors → JSON error
            return JsonResponse({"error": f"Tool error: {str(me)}", "tool": tool_name}, status=400)

        # Print tool data
        print("Tool data:", tool_data.get("data", ""))
        # 4) Summarize tool result with Llama (normal path)
        content = json.dumps(tool_data.get("data", ""), ensure_ascii=False)

        # 5) SSE stream of the summary (reuse same helper)
        return StreamingHttpResponse(
            llama_event_stream(content),
            content_type="text/event-stream",
        )


