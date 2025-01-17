import re

def sanitize_gpt_response(response_str: str) -> str:
    # Remove markdown indicators if present
    response_str = re.sub(r'^```json\s*', '', response_str, flags=re.MULTILINE)
    response_str = re.sub(r'```$', '', response_str, flags=re.MULTILINE)
    
    # Replace Python booleans with JSON booleans
    # Be cautious with simple replacements to avoid altering strings that contain these words.
    # Here, we assume that the JSON keys/values don't contain the exact tokens "True" or "False"
    # outside of boolean contexts. If necessary, refine with regex boundaries.
    response_str = response_str.replace(": False", ": false")
    response_str = response_str.replace(": True", ": true")
    
    return response_str.strip()