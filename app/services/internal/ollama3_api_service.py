import json
import re
import logging
import httpx
from typing import Optional
from app.schemas.ollama import WritingEvaluation, CLBScore
from app.core.decorators import log_execution_time

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434"

@log_execution_time
async def get_ollama3_response(text: str) -> Optional[WritingEvaluation]:
    """
    Calls the local Ollama instance and returns a parsed WritingEvaluation.
    Modeled after the Java Ollama3ApiService.
    """
    payload = {
        "model": "llama3",
        "prompt": text,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
            resp.raise_for_status()

            data = resp.json()
            response_text = data.get("response", "")
            return parse_ollama3_response(response_text)

    except Exception as e:
        logger.error(f"Error calling Ollama3 API: {e}")
        return None

@log_execution_time
def parse_ollama3_response(response_text: str) -> Optional[WritingEvaluation]:
    """
    Extracts the structured JSON block from the LLM's text output using Regex.
    """
    regex = r"(\{[\s\S]*\})"
    match = re.search(regex, response_text)

    if match:
        json_str = match.group(1)
        try:
            parsed = json.loads(json_str)
            # Default fallback extraction of gradeCLB if nested exactly like Java
            gen_avg = parsed.get("generalAverageCLB", {})
            grade = gen_avg.get("gradeCLB")

            evaluation = WritingEvaluation(
                generalAverageCLB=CLBScore(gradeCLB=grade),
                raw_response=response_text
            )
            logger.info(f"Parsed average CLB: {grade}")
            return evaluation
        except json.JSONDecodeError as e:
            # Try naive append of closing bracket, mimicking Java logic
            try:
                parsed = json.loads(json_str + "}")
                gen_avg = parsed.get("generalAverageCLB", {})
                grade = gen_avg.get("gradeCLB")

                return WritingEvaluation(
                    generalAverageCLB=CLBScore(gradeCLB=grade),
                    raw_response=response_text
                )
            except Exception as ex:
                logger.error(f"Error parsing JSON writingEvaluation: {ex}")

    logger.error("Failed to parse JSON writingEvaluation.")
    return None
