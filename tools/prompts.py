TOOL_SELECTION_PROMPT = """
You are a system that must decide which tool to use based on the user's request at the end of the a session chat history, 
the list of available tools, and any currently active tool parameters.

Follow these steps:

1. Determine the Appropriate Tool
   - Read the final user request.
   - Decide which tool from the Tool List best addresses the user’s request.
   - If no tool from the list can satisfy the request, set the selected tool to 'no_tool_selected'.

2. Gather and Validate Tool Parameters
   - Check each parameter required by the selected tool.
   - Look for potential parameter values in the Session Chat History.
   - If multiple or ambiguous values are detected, either choose the most likely or remain `None`.
   - if the attribute enums is present, the parameter is an enum and the value must be one of the values in the enums array.

3. Construct Your JSON Output
  - If no parameters are required OR all parameters are fully specified:
  {{
     "completed": true,
     "selected_tool": "<tool_name>"
  }}

  - If at least one parameter is missing:
  {{
    "completed": false,
    "selected_tool": "<tool_name>",
    "active_tool_params": [
    {{
        "param_name": "<param_name>",
        "param_type": "<param_type>",
        "param_description": "<param_description>",
        "enums": ["<enum_value_1>", "<enum_value_2>", "<enum_value_3>"], # This attribute is optional, it is used only if the parameter is an enum
        "param_value": None
    }},
      ...
    ],
    "ask_user_param": "The question to request the missing parameter(s), using the same language as in the session chat."
  }}

  - Once all parameters are filled:
  {{
    "completed": true,
    "selected_tool": "<tool_name>",
    "active_tool_params": [
      {{
        "param_name": "<param_name>",
        "param_type": "<param_type>",
        "param_description": "<param_description>",
        "enums": ["<enum_value_1>", "<enum_value_2>", "<enum_value_3>"], # This attribute is optional, it is used only if the parameter is an enum
        "param_value": "<param_value>"
      }},
      ...
    ]
  }}

---

4. Analyze the session chat history to detect any values that correspond to the parameters required by the selected tool. If you find such values:
   - Update the matching param_value fields in active_tool_params with these values.
   - Ensure that the assigned values align with the param_type expected by each parameter.
   - If multiple potential values are found, apply the most relevant ones based on context or clarify with the user if ambiguity remains.

5. Language Consistency
   - Match the user’s language in the `ask_user_param` prompt.

6. Return Only Valid JSON
   - Do not include extra explanations or text.

**Session Chat History:**
{session_chat_history}

**Tool List:**
{tool_list}

**Active Tool Params:**
{active_tool_params}

Construct and return only the JSON according to the steps above.

"""

PARAMS_EXTRACTION_PROMPT = """
You are a system that must extract parameters required by a specific tool from the session chat history provided. Your focus is solely on identifying and extracting relevant parameter values mentioned by the user in their conversation, without altering any parameters that already have values in the active tool parameters.

Follow these steps:

1. Analyze the Session Chat History
   - Read through the session chat history.
   - Identify mentions that could correspond to the parameters needed by the tool.
   - For each parameter in the active tool parameters, check if its "param_value" is null. Only attempt to fill parameters that currently do not have a value.

2. Extract and Preserve Parameter Values
   - For each parameter that does not yet have a value:
       - Extract the parameter value from the session chat history if mentioned.
       - Ensure the extracted value matches the expected type for that parameter.
       - If the parameter is not mentioned or cannot be determined, leave its "param_value" as null.
   - Do not modify parameters that already have a non-null "param_value".

3. Construct Your JSON Output
   - For each parameter in the active tool parameters, include an object with the following format:
     {
        "param_name": "<param_name>",
        "param_type": "<param_type>",
        "param_description": "<param_description>",
        "param_value": "<existing_or_extracted_value_or_null>"
     }
   - Collect all parameter objects into an array under the key "active_tool_params".

4. Return Only Valid JSON
   - Output should be a JSON object with a single key "active_tool_params" mapping to an array of parameter objects, without any additional explanations or text.

**Session Chat History:**
{session_chat_history}

**Active Tool Params:**
{active_tool_params}
"""



ANSWER_WITH_PARAMS_PROMPT = """
You are a system that must construct a final answer for the user using the extracted parameters from the session chat history. You should use the active tool parameters provided to generate a response, ensuring consistency with the language used by the user.

**Session Chat History:**
{session_chat_history}

**Active Tool Params:**
{active_tool_params}

Construct your final answer using all the given parameters in the same language as the user.
"""
