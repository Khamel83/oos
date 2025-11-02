#!/usr/bin/env python3
"""
OOS AI Provider Abstraction Layer
Supports OpenRouter, OpenAI, and future AI providers with fallback and load balancing
"""

import os
import json
import httpx
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderType(Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ModelConfig:
    provider: ProviderType
    model_id: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class AIResponse:
    content: str
    model_used: str
    provider: ProviderType
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None


class AIProvider:
    """Abstract base class for AI providers"""

    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> AIResponse:
        raise NotImplementedError

    async def health_check(self) -> bool:
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()


class OpenRouterProvider(AIProvider):
    """OpenRouter AI provider implementation"""

    def __init__(self, api_key: str):
        super().__init__(api_key, "https://openrouter.ai/api/v1")

    async def chat_completion(self, messages: List[Dict], model: str = "openrouter/andromeda-alpha", **kwargs) -> AIResponse:
        """Make chat completion request to OpenRouter"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7)
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Khamel83/oos",
                "X-Title": "OOS - Organized Operational Setup"
            }

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()

            return AIResponse(
                content=data["choices"][0]["message"]["content"],
                model_used=model,
                provider=ProviderType.OPENROUTER,
                tokens_used=data.get("usage", {}).get("total_tokens"),
                cost_estimate=self._estimate_cost(model, data.get("usage", {}))
            )

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if OpenRouter API is accessible"""
        try:
            response = await self.client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            return False

    def _estimate_cost(self, model: str, usage: Dict) -> float:
        """Estimate cost based on model and usage"""
        # Simplified cost estimation - could be enhanced with actual pricing
        cost_per_1k_tokens = {
            "openrouter/andromeda-alpha": 0.0,  # Free model
            "openrouter/gpt-4o": 0.005,
            "openrouter/claude-3-opus": 0.015,
        }

        tokens = usage.get("total_tokens", 0)
        cost_rate = cost_per_1k_tokens.get(model, 0.001)  # Default fallback
        return (tokens / 1000) * cost_rate


class OOSAIManager:
    """Main AI manager with provider fallback and load balancing"""

    def __init__(self):
        self.providers: List[AIProvider] = []
        self.current_provider_index = 0
        self.fallback_enabled = True

        # Initialize providers from environment
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize AI providers from environment variables"""

        # OpenRouter (primary)
        openrouter_key = os.getenv('OPENROUTER_PROJECT_KEY') or os.getenv('OPENROUTER_API_KEY')
        if openrouter_key:
            self.providers.append(OpenRouterProvider(openrouter_key))
            logger.info("Initialized OpenRouter provider")

        if not self.providers:
            raise ValueError("No AI providers configured. Please set OPENROUTER_PROJECT_KEY or OPENROUTER_API_KEY")

    async def chat_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Send chat completion request with automatic fallback"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Default model if not specified
        if not model:
            model = "nvidia/nemotron-nano-12b-v2-vl:free"  # Available free model

        # Try each provider until one succeeds
        for attempt in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]

            try:
                logger.info(f"Attempting AI request with {provider.__class__.__name__}")
                response = await provider.chat_completion(messages, model, **kwargs)

                # Log successful request
                logger.info(f"AI request successful: {response.provider.value}/{response.model_used}")

                return response

            except Exception as e:
                logger.warning(f"Provider {provider.__class__.__name__} failed: {e}")

                # Move to next provider
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)

                # If this is the last provider and all failed, raise exception
                if attempt == len(self.providers) - 1:
                    raise Exception("All AI providers failed")

        raise Exception("No AI providers available")

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all configured providers"""
        results = {}
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            results[provider_name] = await provider.health_check()
        return results

    async def close_all(self):
        """Close all provider connections"""
        for provider in self.providers:
            await provider.close()


# Global AI manager instance
_ai_manager = None


def get_ai_manager() -> OOSAIManager:
    """Get or create global AI manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = OOSAIManager()
    return _ai_manager


async def ask_ai(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """Convenience function for AI requests"""
    manager = get_ai_manager()
    response = await manager.chat_completion(prompt, model, system_prompt, **kwargs)
    return response.content


def create_test_prompt() -> str:
    """Create a test prompt for AI functionality"""
    return "Hello! Please respond with 'OOS AI integration is working correctly' to confirm you're functional."


# Model configuration presets
MODEL_PRESETS = {
    "fast": ModelConfig(
        provider=ProviderType.OPENROUTER,
        model_id="nvidia/nemotron-nano-12b-v2-vl:free",
        max_tokens=2048,
        temperature=0.7
    ),
    "balanced": ModelConfig(
        provider=ProviderType.OPENROUTER,
        model_id="amazon/nova-premier-v1",
        max_tokens=4096,
        temperature=0.7
    ),
    "quality": ModelConfig(
        provider=ProviderType.OPENROUTER,
        model_id="perplexity/sonar-pro-search",
        max_tokens=8192,
        temperature=0.5
    )
}


def get_model_preset(name: str) -> ModelConfig:
    """Get predefined model configuration"""
    return MODEL_PRESETS.get(name, MODEL_PRESETS["fast"])


if __name__ == "__main__":
    # Test the AI integration
    async def test_ai_integration():
        print("🧪 Testing OOS AI Integration...")

        try:
            manager = get_ai_manager()

            # Health check
            print("1. Checking provider health...")
            health = await manager.health_check_all()
            for provider, status in health.items():
                print(f"   {provider}: {'✅' if status else '❌'}")

            # Test basic AI call
            print("\n2. Testing AI response...")
            response = await manager.chat_completion(
                prompt="Say 'OOS AI integration is working!'",
                system_prompt="You are a helpful AI assistant."
            )

            print(f"   Provider: {response.provider.value}")
            print(f"   Model: {response.model_used}")
            print(f"   Response: {response.content}")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost_estimate or 0:.6f}")

            print("\n✅ AI integration test completed successfully!")

        except Exception as e:
            print(f"❌ AI integration test failed: {e}")

        finally:
            if 'manager' in locals():
                await manager.close_all()

    asyncio.run(test_ai_integration())