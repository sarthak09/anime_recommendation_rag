from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["HUGGINGFACEHUB_API_TOKEN"]=os.getenv("HUGGINGFACEHUB_API_TOKEN")

class LLM:
    def __init__(self, model_name: str):
        # Initialize model
        self.llm = init_chat_model(model=model_name)

    def llmtest(self, prompt="Hello how are you?"):
        print(self.llm.invoke(prompt).content)
