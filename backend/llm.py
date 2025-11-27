from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key

hf_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if hf_key:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_key



class LLM:
    def __init__(self, model_name: str):
        self.llm = init_chat_model(model=model_name)

    def llmtest(self, prompt="Hello how are you?"):
        print(self.llm.invoke(prompt).content)
