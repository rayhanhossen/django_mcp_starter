import torch
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v0.4"
HF_TOKEN = "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"

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


async def summarize_with_llama_local(content: str, max_new_tokens: int = 256, temperature: float = 0.2) -> str:
    """
    Summarize text using local TinyLlama-1.1B-Chat-v0.4 model (async wrapper).
    """

    def _generate():
        prompt = f"You are a concise assistant. Summarize the following:\n\n{content}\n\nSummary:"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=False,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3
        )
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "Summary:" in summary:
            summary = summary.split("Summary:")[-1].strip()
        return summary

    return await asyncio.to_thread(_generate)
