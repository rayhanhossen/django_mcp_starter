import threading

import torch
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v0.4"
HF_TOKEN = ""

# Load model/tokenizer once at startup
print(f"Loading model {MODEL_ID}... This may take 1-3 minutes on first run.")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)

# Load with Apple MPS (Metal) if available
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float16 if device.type == "mps" else torch.float32,
    device_map={"": device.type},  # send to MPS or CPU
    token=HF_TOKEN,
)


async def summarize_with_llama_local(content: str, max_new_tokens: int = 256, temperature: float = 0.7):
    """
    Summarize text using local TinyLlama-1.1B-Chat-v0.4 model (async wrapper).
    """
    prompt = f"You are a concise assistant. Summarize the following:\n\n{content}\n\nSummary:"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True,
    )

    gen_kwargs = dict(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,  # deterministic like your original
        repetition_penalty=1.2,
        no_repeat_ngram_size=3,
        eos_token_id=tokenizer.eos_token_id,
        streamer=streamer,
    )
    # Run generation in a background thread so we can iterate the streamer
    thread = threading.Thread(target=model.generate, kwargs=gen_kwargs, daemon=True)
    thread.start()

    loop = asyncio.get_running_loop()

    # Pull chunks from the streamer without blocking the event loop
    def _next_chunk():
        try:
            return next(streamer)
        except StopIteration:
            return None

    while True:
        chunk = await loop.run_in_executor(None, _next_chunk)
        if chunk is None:
            break
        yield chunk

    thread.join()
