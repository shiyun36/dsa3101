from dotenv import load_dotenv
import os
from openai import OpenAI



def ask_llm(esg_category,data,table_data,prompts_func):
    load_dotenv('secret.env')

    API_KEY = os.getenv('API_KEY')

    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    )
    jsons = [] #create list to store llm response
    for i in esg_category: #Run LLM 3 Times according to E,S,G to prevent hallucination
        df = data[data['esg_cat'] == i].to_json()
        prompts = prompts_func(df,table_data)
        completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        extra_body={},
        model="google/gemini-2.0-pro-exp-02-05:free",
        messages=[
            {
            "role": "user",
            "content": prompts
            },
        ]
        )
        print(completion.choices[0].message.content)
        jsons.append(completion.choices[0].message.content)
    return jsons