import os
import yaml
from pathlib import Path

from openai import AsyncOpenAI
import instructor

def getValue(key):
    value = os.getenv(key)

    if value == None:
        with open('src/env.yaml', 'r') as file:
            data = yaml.safe_load(file)

        value = data[key]

    return value

def params_to_token(extracted_terms):
    query = ""

    for term in extracted_terms:
        if len(query) > 0:
            query += ';'
        current_query = ''
        if (s := term.get('scope', '')) != '':
            current_query += s + ":"
            if (f := term.get('field', '')) != '':
                current_query += f+ ":"
        if (v := term.get('value', '')) != '':
            current_query += v
    
        query += current_query

    return query

def generate_prompt(fileName, additional_info):
    prompt =  """
        {system_prompt}

        # Additional Info

        {additional_info}
    """

    # system_prompt = importlib.resources.files().joinpath("../resources/system_prompt.md").read_text()
    system_prompt = (Path(__file__).parent / "prompts" / fileName).read_text()

    prompt = prompt.format(
        system_prompt=system_prompt,
        additional_info=additional_info
    ).strip()

    return prompt

def add_client(state):
    client = AsyncOpenAI(api_key=getValue("OPEN_API_KEY"), base_url=getValue("OPENAI_BASE_URL"))
    instructor_client = instructor.patch(client)
    state["instructor_client"] = instructor_client