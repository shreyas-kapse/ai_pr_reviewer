from langchain_google_genai import ChatGoogleGenerativeAI
from enums import ModelEnum
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

class LLMService:

    _llm = None

    # @classmethod
    # def get_llm(cls):
    #     if cls._llm is None:
    #         cls._llm = ChatGoogleGenerativeAI(
    #             model=ModelEnum.Google_Gemini_3_Flash_Preview
    #         )
    #     return cls._llm
    
    # to get local llm
    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            cls._llm = ChatOllama(
                 model=ModelEnum.PHI3,
                temperature =0.7,
                device = "cpu",
                format="json",
                num_predict=-1,
                max_tokens=1000,
                
            )
        return cls._llm