import json
import logging
from typing import Any, Sequence
from mcp.server.fastmcp import FastMCP
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_vocab_server")

# Path to the vocabulary file
VOCAB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vocabulary.json")

# Initialize FastMCP Server
mcp = FastMCP("NorskVocabServer")

def load_vocabulary() -> list[dict[str, Any]]:
    """Loads the vocabulary data from JSON."""
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("words", [])
    except Exception as e:
        logger.error(f"Failed to load vocabulary: {e}")
        return []

@mcp.tool()
def lookup_word(word: str) -> str:
    """
    Looks up a Norwegian word in the vocabulary list and returns its definition, 
    English translation, and an example sentence.
    
    Args:
        word: The Norwegian word to look up.
        
    Returns:
        A string containing the formatted definition and example, or a message if not found.
    """
    vocab = load_vocabulary()
    
    word_lower = word.lower()
    for item in vocab:
        if item.get("norwegian", "").lower() == word_lower:
            en = item.get("english", "")
            ex_no = item.get("example_no", "")
            ex_en = item.get("example_en", "")
            pronunciation = item.get("pronunciation", "")
            
            result = f"Mening/Oversettelse (English): {en}\n"
            if pronunciation:
                result += f"Uttale (Pronunciation): {pronunciation}\n"
            if ex_no and ex_en:
                result += f"Eksempel: {ex_no} ({ex_en})\n"
                
            return result
            
    return f"Beklager, jeg fant ikke ordet '{word}' i ordboken."

@mcp.resource("vocabulary://{word}")
def get_vocabulary_entry(word: str) -> str:
    """
    Resource endpoint to get a specific vocabulary entry by word.
    """
    vocab = load_vocabulary()
    word_lower = word.lower()
    for item in vocab:
        if item.get("norwegian", "").lower() == word_lower:
            return json.dumps(item, indent=2, ensure_ascii=False)
            
    return json.dumps({"error": "Word not found"})

if __name__ == "__main__":
    logger.info("Starting NorskVocabServer MCP Server via stdio")
    mcp.run(transport="stdio")
