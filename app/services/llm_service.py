from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from services.config_service import ConfigService
import os


load_dotenv()

class LLMService:
    _llm = None
    @classmethod
    def get_llm(cls):
        if cls._llm is not None:
            return cls._llm

        config = ConfigService.get_config()
        llm_config = config["llm"]
        provider = llm_config["provider"]

        print(f"\n Using provider: {provider}")

        if provider == "ollama":
            ollama_config = llm_config["ollama"]
            cls._llm = ChatOllama(
                model=ollama_config["model"],
                temperature=ollama_config["temperature"],
                num_ctx=ollama_config["num_ctx"],
                device=ollama_config["device"]
            )
            return cls._llm

        if provider == "gemini":
            gemini_config = llm_config["gemini"]
            cls._llm = (
                ChatGoogleGenerativeAI(
                    model=gemini_config["model"],
                    temperature=gemini_config["temperature"],
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            )
            return cls._llm
        raise ValueError(f"Unsupported provider: {provider}")