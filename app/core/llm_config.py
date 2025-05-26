from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, PrivateAttr
from typing import Optional

class LangchainLLMConfig(BaseSettings):
    # Azure OpenAI Configs
    azure_openai_api_key: SecretStr = Field(..., validation_alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(..., validation_alias="AZURE_OPENAI_API_VERSION")
    azure_openai_endpoint: str = Field(..., validation_alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: str = Field(..., validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME")

    # Embedding Configs
    azure_openai_embed_api_endpoint: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_API_ENDPOINT")
    azure_openai_embed_api_key: SecretStr = Field(..., validation_alias="AZURE_OPENAI_EMBED_API_KEY")
    azure_openai_embed_model: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_MODEL")
    azure_openai_embed_version: str = Field(..., validation_alias="AZURE_OPENAI_EMBED_VERSION")

    _langchain_llm: Optional[AzureChatOpenAI] = PrivateAttr(default=None)
    _langchain_embedding: Optional[AzureOpenAIEmbeddings] = PrivateAttr(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def init_langchain(self) -> None:
        """Initialize Langchain components with Azure OpenAI"""
        self._langchain_llm = AzureChatOpenAI(
            deployment_name=self.azure_openai_deployment_name,
            openai_api_key=self.azure_openai_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_endpoint,
            openai_api_version=self.azure_openai_api_version
        )

        self._langchain_embedding = AzureOpenAIEmbeddings(
            azure_deployment=self.azure_openai_embed_model,
            openai_api_key=self.azure_openai_embed_api_key.get_secret_value(),
            azure_endpoint=self.azure_openai_embed_api_endpoint,
            openai_api_version=self.azure_openai_embed_version,
            chunk_size=1000
        )

    @property
    def langchain_llm(self) -> AzureChatOpenAI:
        if self._langchain_llm is None:
            self.init_langchain()
        return self._langchain_llm

    @property
    def langchain_embedding(self) -> AzureOpenAIEmbeddings:
        if self._langchain_embedding is None:
            self.init_langchain()
        return self._langchain_embedding
