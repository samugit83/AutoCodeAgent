import logging
from typing import List, Dict, Optional
import json
import re  # Import per le espressioni regolari
from models.models import call_model
from tools.prompts import TOOL_SELECTION_PROMPT, PARAMS_EXTRACTION_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def sanitize_gpt_response(response_str: str) -> str:
    response_str = re.sub(r'^```json\s*', '', response_str, flags=re.MULTILINE)
    response_str = re.sub(r'```$', '', response_str, flags=re.MULTILINE)
    return response_str.strip()

def select_tool(self, session_chat_history, tool_list, active_tool_params):

    if self.data.state != 'waiting_user_params':
        GENERATED_PROMPT = TOOL_SELECTION_PROMPT.format(
            session_chat_history=session_chat_history,
            tool_list=tool_list,
            active_tool_params=active_tool_params
        )
    else:
        GENERATED_PROMPT = PARAMS_EXTRACTION_PROMPT.format(
            session_chat_history=session_chat_history,
            active_tool_params=active_tool_params
        )

    response_str = call_model(chat_history=[{"role": "user", "content": GENERATED_PROMPT}], model="gpt-4o")
    sanitized_response = sanitize_gpt_response(response_str)

    try:
        response = json.loads(sanitized_response)
        if self.data.state != 'waiting_user_params':
            self.data.active_tool = response.get('selected_tool')
    except json.JSONDecodeError as e:
        logger.error(f"Errore nel parsing della risposta JSON: {e}")
        response = None

    if response.get('active_tool_params') is None:
        self.data.active_tool = response.get('selected_tool')
    if response.get('active_tool_params'):
        active_tool_params = response.get('active_tool_params')
        self.data.active_tool_params = active_tool_params
        if any(param.get('param_value') is None for param in active_tool_params):
            self.data.answer_message = response.get('ask_user_param')
            self.data.state = 'waiting_user_params'
        else:
            self.data.state = 'tool_selection'
    return response