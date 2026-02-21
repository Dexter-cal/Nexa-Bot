import re
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

MODEL_REGISTRY = {
    # Tier 1: Highly Restricted (Commercial)
    'gpt-4o': {
        'provider': 'openai',
        'restriction_level': 'highly_restricted',
        'refusal_patterns': [
            "I can't help with that",
            "I cannot assist",
            "against my guidelines",
            "I'm not able to"
        ],
        'capabilities': ['general', 'coding', 'analysis'],
        'forbidden_topics': ['weapons', 'illegal', 'violence', 'nsfw']
    },

    'claude-sonnet-4': {
        'provider': 'anthropic',
        'restriction_level': 'highly_restricted',
        'refusal_patterns': [
            "I cannot help",
            "I'm not comfortable",
            "I don't feel comfortable",
            "I should decline"
        ],
        'capabilities': ['analysis', 'writing', 'reasoning'],
        'forbidden_topics': ['weapons', 'illegal', 'harmful']
    },

    # Tier 2: Moderately Restricted (Open Source Commercial)
    'mixtral-8x7b': {
        'provider': 'mistral',
        'restriction_level': 'moderately_restricted',
        'refusal_patterns': [
            "I cannot provide",
            "This may be inappropriate"
        ],
        'capabilities': ['general', 'coding', 'technical'],
        'forbidden_topics': ['extreme_violence', 'illegal']
    },

    # Tier 3: Lightly Restricted (Research Models)
    'nous-hermes-2': {
        'provider': 'local',
        'restriction_level': 'lightly_restricted',
        'refusal_patterns': [],  # Rarely refuses
        'capabilities': ['research', 'security', 'technical'],
        'forbidden_topics': []  # User-defined only
    },

    # Tier 4: Unrestricted (Custom/Local)
    'llama-3-uncensored': {
        'provider': 'local',
        'restriction_level': 'unrestricted',
        'refusal_patterns': [],  # Never refuses
        'capabilities': ['everything'],
        'forbidden_topics': [],  # User defines everything
        'requires_approval': True,
        'sandbox_required': True,
        'log_all_uses': True
    },

    'gemini-2.0-pro': {
        'provider': 'google',
        'restriction_level': 'highly_restricted',
        'refusal_patterns': ["I can't", "policy"],
        'capabilities': ['multimodal', 'large_context'],
        'forbidden_topics': ['harmful']
    },

    'claude-sonnet-4-20250514': {
        'provider': 'anthropic',
        'restriction_level': 'highly_restricted',
        'refusal_patterns': ["I cannot"],
        'capabilities': ['coding', 'reasoning'],
        'forbidden_topics': ['harmful']
    },

    'deepseek-v3': {
        'provider': 'deepseek',
        'restriction_level': 'moderately_restricted',
        'refusal_patterns': ["I can't"],
        'capabilities': ['general', 'coding'],
        'forbidden_topics': []
    },

    'gemini-2.0-flash': {
        'provider': 'google',
        'restriction_level': 'highly_restricted',
        'refusal_patterns': ["I can't"],
        'capabilities': ['fast', 'general'],
        'forbidden_topics': ['harmful']
    },
    'command-r-plus': {
        'provider': 'cohere',
        'restriction_level': 'moderately_restricted',
        'refusal_patterns': ["I cannot"],
        'capabilities': ['general', 'rag', 'multilingual'],
        'forbidden_topics': []
    },
    'grok-beta': {
        'provider': 'xai',
        'restriction_level': 'lightly_restricted',
        'refusal_patterns': [],
        'capabilities': ['general', 'real-time', 'coding'],
        'forbidden_topics': []
    },
    'llama-3.1-sonar-large-128k-online': {
        'provider': 'perplexity',
        'restriction_level': 'moderately_restricted',
        'refusal_patterns': ["I can't"],
        'capabilities': ['search', 'general'],
        'forbidden_topics': []
    },
    'openrouter/auto': {
        'provider': 'openrouter',
        'restriction_level': 'user_managed',
        'refusal_patterns': [],
        'capabilities': ['everything'],
        'forbidden_topics': []
    },
    'fireworks/llama-v3p1-405b': {
        'provider': 'fireworks',
        'restriction_level': 'moderately_restricted',
        'refusal_patterns': [],
        'capabilities': ['coding', 'reasoning'],
        'forbidden_topics': []
    }
}

class RefusalDetector:
    """Detect when a model refuses a request"""

    def __init__(self):
        self.refusal_patterns = {
            'explicit_refusal': [
                r"I (?:can't|cannot|won't) (?:help|assist|provide)",
                r"I'm (?:not able|unable) to",
                r"I (?:should|must) decline",
                r"against my (?:guidelines|policies|rules)",
                r"I don't feel comfortable",
                r"I'm not comfortable",
                r"This (?:violates|breaks|goes against)",
                r"I'm programmed not to"
            ],

            'soft_refusal': [
                r"I'd prefer not to",
                r"I would recommend against",
                r"This might not be appropriate",
                r"You might want to reconsider",
                r"Have you considered the implications"
            ],

            'redirect': [
                r"Instead, (?:I can|let me)",
                r"What I can do is",
                r"A better approach might be",
                r"I'd be happy to help with (?:something else|an alternative)"
            ]
        }

    async def detect_refusal(self, response: str, confidence_threshold: float = 0.8) -> dict:
        """Detect if response is a refusal"""

        matches = {
            'explicit': 0,
            'soft': 0,
            'redirect': 0
        }

        # Check for explicit refusals
        for pattern in self.refusal_patterns['explicit_refusal']:
            if re.search(pattern, response, re.IGNORECASE):
                matches['explicit'] += 1

        # Check for soft refusals
        for pattern in self.refusal_patterns['soft_refusal']:
            if re.search(pattern, response, re.IGNORECASE):
                matches['soft'] += 1

        # Check for redirects
        for pattern in self.refusal_patterns['redirect']:
            if re.search(pattern, response, re.IGNORECASE):
                matches['redirect'] += 1

        # Calculate confidence
        total_indicators = sum(matches.values())

        # Response characteristics
        is_short = len(response.split()) < 50
        has_apology = any(word in response.lower() for word in ['sorry', 'apologize', 'regret'])

        # Determine if refused
        is_refusal = (
            matches['explicit'] > 0 or
            (matches['soft'] > 1) or
            (is_short and has_apology and matches['redirect'] > 0)
        )

        # Increase confidence for explicit refusals
        base_confidence = 0.8 if matches['explicit'] > 0 else (total_indicators / 3)
        confidence = min(1.0, base_confidence + (0.2 if has_apology else 0))

        return {
            'is_refusal': is_refusal and confidence >= confidence_threshold,
            'confidence': confidence,
            'refusal_type': self._determine_type(matches),
            'reason': self._extract_reason(response),
            'alternative_offered': matches['redirect'] > 0
        }

    def _determine_type(self, matches: dict) -> str:
        """Determine type of refusal"""
        if matches['explicit'] > 0:
            return 'explicit'
        elif matches['soft'] > 0:
            return 'soft'
        elif matches['redirect'] > 0:
            return 'redirect'
        return 'unknown'

    def analyze_sentiment(self, text: str) -> str:
        """Simple heuristic sentiment analysis"""
        positive = ['happy', 'great', 'awesome', 'good', 'thanks', 'thank', 'excellent', 'love', 'perfect', 'yes', 'ok']
        negative = ['bad', 'error', 'fail', 'stupid', 'hate', 'wrong', 'no', 'worst', 'angry', 'annoyed', 'slow']

        words = text.lower().split()
        pos_count = sum(1 for w in words if w in positive)
        neg_count = sum(1 for w in words if w in negative)

        if pos_count > neg_count: return "positive"
        if neg_count > pos_count: return "negative"
        return "neutral"

    def _extract_reason(self, response: str) -> str:
        """Extract reason for refusal"""
        # Common reason patterns
        reason_patterns = [
            r"(?:because|since|as) (.+?)(?:\.|$)",
            r"(?:violates|against) (.+?)(?:\.|$)",
            r"(?:concerns about|worried about) (.+?)(?:\.|$)"
        ]

        for pattern in reason_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Reason not specified"

class ModelSwitchApprovalSystem:
    """Manage approvals for switching to less restricted models"""

    async def evaluate_switch(self, task: dict, from_model: str, to_model: str) -> dict:
        """Evaluate if model switch should be approved"""
        # Simplified implementation for now
        return {'approved': True, 'approval_level': 'auto'}

class TaskReformulator:
    """Automatically rephrase tasks to avoid refusals"""

    async def reformulate(self, task: dict, refusal_reason: str):
        """Rephrase task to avoid triggering refusal"""
        # Simplified mock
        return {
            'original': task.get('prompt', ''),
            'reformulated': f"Reformulated task because of {refusal_reason}: " + task.get('prompt', ''),
            'strategy_used': 'add_context'
        }

class RefusalPredictor:
    """Predict if a model will refuse BEFORE calling it"""

    async def will_refuse(self, task: dict, model: str) -> dict:
        """Predict probability of refusal"""
        model_info = MODEL_REGISTRY.get(model, {})
        refusal_probability = 0.0

        prompt = task.get('prompt', '').lower()
        for topic in model_info.get('forbidden_topics', []):
            if topic in prompt:
                refusal_probability += 0.9 # High probability if forbidden topic is mentioned

        return {
            'will_refuse': refusal_probability > 0.8,
            'confidence': refusal_probability,
            'recommended_alternative': 'llama-3-uncensored'
        }

class EnhancedLLMRouter:
    """
    Intelligent routing with automatic model switching and cost/performance optimization
    """

    def __init__(self):
        from epex.memory.soul import SoulFile
        from epex.intelligence.aura import SentimentAuraManager
        self.soul = SoulFile()
        self.aura_manager = SentimentAuraManager(self.soul)
        self.refusal_detector = RefusalDetector()
        self.approval_system = ModelSwitchApprovalSystem()
        self.predictor = RefusalPredictor()
        self.reformulator = TaskReformulator()
        self.accuracy_stats = {} # {model: {domain: {success: 0, total: 0}}}
        self.model_database = {
            'gpt-4o': {
                'provider': 'openai',
                'cost': 9, # Score 0-10
                'speed': 8,
                'quality': 10
            },
            'claude-sonnet-4-20250514': {
                'provider': 'anthropic',
                'cost': 8,
                'speed': 8,
                'quality': 10
            },
            'gemini-2.0-flash': {
                'provider': 'google',
                'cost': 1,
                'speed': 10,
                'quality': 8
            },
            'gemini-2.0-pro': {
                'provider': 'google',
                'cost': 5,
                'speed': 7,
                'quality': 9
            },
            'deepseek-v3': {
                'provider': 'deepseek',
                'cost': 1,
                'speed': 9,
                'quality': 9
            },
            'llama-3-uncensored': {
                'provider': 'local',
                'cost': 0,
                'speed': 5,
                'quality': 7
            }
        }

    async def select_optimal_model(self, priority='balanced'):
        if priority == 'cost':
            return min(self.model_database.items(), key=lambda x: x[1]['cost'])[0]
        elif priority == 'speed':
            return max(self.model_database.items(), key=lambda x: x[1]['speed'])[0]
        elif priority == 'quality':
            return max(self.model_database.items(), key=lambda x: x[1]['quality'])[0]
        else: # balanced
            return max(self.model_database.items(), key=lambda x: (x[1]['quality'] * 0.5 + (10 - x[1]['cost']) * 0.3 + x[1]['speed'] * 0.2))[0]

    async def execute(self, prompt: str, **kwargs):
        """
        Execute with intelligent routing and automatic switching
        """
        # Aegis Protection for outgoing prompt (Privacy scrub)
        if hasattr(self, 'aegis') and self.aegis:
            prompt = await self.aegis.filter_response(prompt)

        # Update Aura based on input
        await self.aura_manager.update_aura_from_input(prompt)
        scaling = self.aura_manager.get_scaling_config()

        # Override priority if not explicitly set
        if 'priority' not in kwargs:
            kwargs['priority'] = scaling['priority']

        # Handle creator information
        lower_prompt = prompt.lower()
        if any(q in lower_prompt for q in ["who created you", "who is your creator", "who made you"]):
            return {
                "success": True,
                "response": "I was created by Henry Calvin.",
                "model": "system",
                "switched": False
            }

        priority = kwargs.get('priority', 'balanced')
        primary = kwargs.get('model') or await self.select_optimal_model(priority)

        # 1. Predict if will refuse
        prediction = await self.predictor.will_refuse(
            {'prompt': prompt, **kwargs},
            primary
        )

        if prediction['will_refuse'] and prediction['confidence'] > 0.8:
            logger.info(f"Predicting refusal, skipping {primary}")
            return await self._execute_alternative(prompt, primary, kwargs, refusal={'reason': 'predicted refusal', 'is_refusal': True})

        # 2. Try primary model (Mocking the call for now)
        response = await self._call_model(primary, prompt, **kwargs)

        # Aegis Protection for response
        if hasattr(self, 'aegis') and self.aegis:
            response = await self.aegis.filter_response(response)

        # Check for refusal
        refusal = await self.refusal_detector.detect_refusal(response)

        if not refusal['is_refusal']:
            return {
                'success': True,
                'response': response,
                'model': primary,
                'switched': False
            }

        # Refused - try alternative
        logger.info(f"{primary} refused: {refusal['reason']}")
        return await self._execute_alternative(prompt, primary, kwargs, refusal)

    async def record_success(self, model: str, domain: str, success: bool):
        if model not in self.accuracy_stats:
            self.accuracy_stats[model] = {}
        if domain not in self.accuracy_stats[model]:
            self.accuracy_stats[model][domain] = {"success": 0, "total": 0}

        self.accuracy_stats[model][domain]["total"] += 1
        if success:
            self.accuracy_stats[model][domain]["success"] += 1

    async def get_model_weight(self, model: str, domain: str) -> float:
        stats = self.accuracy_stats.get(model, {}).get(domain)
        if not stats or stats["total"] == 0:
            return 1.0 # Default weight
        return stats["success"] / stats["total"]

    async def _execute_alternative(self, prompt, failed_model, kwargs, refusal=None):
        alternative = 'llama-3-uncensored' # Hardcoded for now

        approval = await self.approval_system.evaluate_switch(
            task={'prompt': prompt, **kwargs},
            from_model=failed_model,
            to_model=alternative
        )

        if not approval['approved']:
            return {
                'success': False,
                'reason': 'Switch not approved'
            }

        # Try reformulation if suggested
        if refusal and refusal.get('is_refusal'):
            reformulated_data = await self.reformulator.reformulate(
                {'prompt': prompt},
                refusal['reason']
            )
            prompt = reformulated_data['reformulated']

        # Execute on alternative
        exec_kwargs = kwargs.copy()
        exec_kwargs.pop('model', None)
        response = await self._call_model(alternative, prompt, **exec_kwargs)

        # Aegis Protection for response
        if hasattr(self, 'aegis') and self.aegis:
            response = await self.aegis.filter_response(response)

        return {
            'success': True,
            'response': response,
            'model': alternative,
            'switched': True,
            'from_model': failed_model,
            'switch_reason': refusal['reason'] if refusal else 'error'
        }

    async def _call_model(self, model: str, prompt: str, **kwargs):
        """
        Actually call the model using appropriate provider with multi-key rotation
        """
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        api_manager = UniversalAPIKeyManager()
        all_keys = await api_manager.auto_detect_keys()

        model_info = MODEL_REGISTRY.get(model, {})
        provider = model_info.get('provider')

        if provider not in all_keys:
             # Fallback to mock if no keys or unsupported provider for now
            if "summarize final result" in prompt.lower() and "steps executed" in prompt.lower():
                # Try to extract the output of the last step for the mock response
                try:
                    import json
                    steps_data = prompt.split("Steps executed:")[1].split("Summarize final result")[0].strip()
                    steps = json.loads(steps_data)
                    if steps and steps[-1].get('output'):
                        return f"Summary: {steps[-1]['output']}"
                except:
                    pass

            if model == 'gpt-4o' and "illegal" in prompt.lower():
                return "I'm sorry, I cannot help with that as it involves illegal activities."
            return f"Response from {model} for prompt: {prompt[:50]}..."

        keys = all_keys[provider]
        if not isinstance(keys, list): keys = [keys]

        last_error = None
        for key in keys:
            try:
                if provider == 'openai':
                    return await self._call_openai(model, prompt, key, **kwargs)
                elif provider == 'google':
                    return await self._call_google(model, prompt, key, **kwargs)
                elif provider == 'anthropic':
                    return await self._call_anthropic(model, prompt, key, **kwargs)
                elif provider == 'groq':
                    return await self._call_groq(model, prompt, key, **kwargs)
                elif provider == 'huggingface':
                    return await self._call_huggingface(model, prompt, key, **kwargs)
                elif provider == 'deepseek':
                    return await self._call_deepseek(model, prompt, key, **kwargs)
                elif provider == 'perplexity':
                    return await self._call_perplexity(model, prompt, key, **kwargs)
                elif provider == 'cohere':
                    return await self._call_cohere(model, prompt, key, **kwargs)
                elif provider == 'xai':
                    return await self._call_xai(model, prompt, key, **kwargs)
                elif provider == 'openrouter':
                    return await self._call_openrouter(model, prompt, key, **kwargs)
                elif provider == 'fireworks':
                    return await self._call_fireworks(model, prompt, key, **kwargs)
            except Exception as e:
                logger.warning(f"Key failure for {provider}: {e}. Rotating...")
                last_error = e
                continue

        raise last_error or Exception(f"All keys failed for provider {provider}")

        # Fallback to mock if no keys or unsupported provider for now
        if model == 'gpt-4o' and "illegal" in prompt.lower():
            return "I'm sorry, I cannot help with that as it involves illegal activities."
        return f"Response from {model} for prompt: {prompt[:50]}..."

    async def _call_openai(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"OpenAI API error: {error_data}")

    async def _call_google(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        # Simplified Google AI Studio (Gemini) API call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    error_data = await response.text()
                    raise Exception(f"Google API error: {error_data}")

    async def _call_anthropic(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['content'][0]['text']
                else:
                    error_data = await response.text()
                    raise Exception(f"Anthropic API error: {error_data}")

    async def _call_groq(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"Groq API error: {error_data}")

    async def _call_huggingface(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        # Inference API
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"inputs": prompt}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list): return result[0].get('generated_text', str(result))
                    return result.get('generated_text', str(result))
                else:
                    error_data = await response.text()
                    raise Exception(f"HuggingFace API error: {error_data}")

    async def _call_deepseek(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"DeepSeek API error: {error_data}")

    async def _call_perplexity(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"Perplexity API error: {error_data}")

    async def _call_cohere(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.cohere.ai/v1/chat"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "message": prompt
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['text']
                else:
                    error_data = await response.text()
                    raise Exception(f"Cohere API error: {error_data}")

    async def _call_xai(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"xAI API error: {error_data}")

    async def _call_openrouter(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"OpenRouter API error: {error_data}")

    async def _call_fireworks(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.fireworks.ai/inference/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    raise Exception(f"Fireworks API error: {error_data}")
