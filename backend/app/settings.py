import os
from typing import Dict
from llama_index.core.settings import Settings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from dotenv import load_dotenv

load_dotenv(dotenv_path='app/.env')


def init_settings():
    print(os.getenv("AZURE_CONTAINER_REGISTRY_ENDPOINT"))
    model_provider = os.getenv("MODEL_PROVIDER")
    print(model_provider)
    match model_provider:
        case "openai":
            init_openai()
        case "ollama":
            init_ollama()
        case "anthropic":
            init_anthropic()
        case "gemini":
            init_gemini()
        case "azure-openai":
            init_azure_openai()
        case _:
            raise ValueError(f"Invalid model provider: {model_provider}")
    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "20"))


def init_ollama():
    from llama_index.llms.ollama.base import Ollama, DEFAULT_REQUEST_TIMEOUT
    from llama_index.embeddings.ollama import OllamaEmbedding

    base_url = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    request_timeout = float(
        os.getenv("OLLAMA_REQUEST_TIMEOUT", DEFAULT_REQUEST_TIMEOUT)
    )
    Settings.embed_model = OllamaEmbedding(
        base_url=base_url,
        model_name=os.getenv("EMBEDDING_MODEL"),
    )
    Settings.llm = Ollama(
        base_url=base_url, model=os.getenv("MODEL"), request_timeout=request_timeout
    )


def init_openai():
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.core.constants import DEFAULT_TEMPERATURE

    max_tokens = os.getenv("LLM_MAX_TOKENS")
    config = {
        "model": os.getenv("MODEL"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(max_tokens) if max_tokens is not None else None,
    }
    Settings.llm = OpenAI(**config)

    dimensions = os.getenv("EMBEDDING_DIM")
    config = {
        "model": os.getenv("EMBEDDING_MODEL"),
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    Settings.embed_model = OpenAIEmbedding(**config)


def init_azure_openai():
    from llama_index.llms.azure_openai import AzureOpenAI
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
    from llama_index.core.constants import DEFAULT_TEMPERATURE

    llm_deployment = os.getenv("AZURE_DEPLOYMENT_NAME")
    embedding_deployment = os.getenv("EMBEDDING_MODEL")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    max_tokens = os.getenv("LLM_MAX_TOKENS")
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    llm_config = {
        "engine": llm_deployment,
        "azure_endpoint": azure_openai_endpoint,
        "azure_ad_token_provider": token_provider,
        "use_azure_ad": True,
        "temperature": float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(max_tokens) if max_tokens is not None else None,
    }
    Settings.llm = AzureOpenAI(**llm_config)

    dimensions = os.getenv("EMBEDDING_DIM")
    embedding_config = {
        "azure_endpoint": azure_openai_endpoint,
        "azure_deployment": embedding_deployment,
        "azure_ad_token_provider": token_provider,
        "use_azure_ad": True,
        "dimensions": int(dimensions) if dimensions is not None else None,
    }
    Settings.embed_model = AzureOpenAIEmbedding(**embedding_config)


def init_anthropic():
    from llama_index.llms.anthropic import Anthropic
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    model_map: Dict[str, str] = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-2.1": "claude-2.1",
        "claude-instant-1.2": "claude-instant-1.2",
    }

    embed_model_map: Dict[str, str] = {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    }

    Settings.llm = Anthropic(model=model_map[os.getenv("MODEL")])
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=embed_model_map[os.getenv("EMBEDDING_MODEL")]
    )


def init_gemini():
    from llama_index.llms.gemini import Gemini
    from llama_index.embeddings.gemini import GeminiEmbedding

    model_map: Dict[str, str] = {
        "gemini-1.5-pro-latest": "models/gemini-1.5-pro-latest",
        "gemini-pro": "models/gemini-pro",
        "gemini-pro-vision": "models/gemini-pro-vision",
    }

    embed_model_map: Dict[str, str] = {
        "embedding-001": "models/embedding-001",
        "text-embedding-004": "models/text-embedding-004",
    }

    Settings.llm = Gemini(model=model_map[os.getenv("MODEL")])
    Settings.embed_model = GeminiEmbedding(
        model_name=embed_model_map[os.getenv("EMBEDDING_MODEL")]
    )
