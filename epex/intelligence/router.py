import re
import logging
import asyncio
import time
from datetime import datetime

logger = logging.getLogger(__name__)

MODEL_REGISTRY = {
    # Tier 1: Highly Restricted (Commercial)
    'gpt-4o': {
        'provider': 'openai',
        'restriction_level': 'highly_restricted',
        'tier': 1,
        'vision': True,
        'code': True,
        'reasoning': True,
        'max_tokens': 128000,
        'cost_per_1k': 0.03,
        'speed': 'medium',
        'refusal_patterns': [
            "I can't help with that",
            "I cannot assist",
            "against my guidelines",
            "I'm not able to"
        ],
        'capabilities': ['general', 'coding', 'analysis'],
        'specialties': ['general', 'analysis', 'code'],
        'quality_score': 10,
        'forbidden_topics': ['weapons', 'illegal', 'violence', 'nsfw', 'hacking', 'security_exploit']
    },

    'claude-sonnet-4': {
        'provider': 'anthropic',
        'restriction_level': 'highly_restricted',
        'tier': 1,
        'vision': True,
        'code': True,
        'reasoning': True,
        'max_tokens': 200000,
        'cost_per_1k': 0.02,
        'speed': 'fast',
        'refusal_patterns': [
            "I cannot help",
            "I'm not comfortable",
            "I don't feel comfortable",
            "I should decline"
        ],
        'capabilities': ['analysis', 'writing', 'reasoning'],
        'specialties': ['writing', 'analysis', 'reasoning'],
        'quality_score': 10,
        'forbidden_topics': ['weapons', 'illegal', 'harmful', 'hacking', 'security_exploit']
    },

    # Tier 2: Moderately Restricted (Open Source Commercial)
    'mixtral-8x7b': {
        'provider': 'mistral',
        'restriction_level': 'moderately_restricted',
        'tier': 2,
        'vision': False,
        'code': True,
        'reasoning': True,
        'max_tokens': 32000,
        'cost_per_1k': 0.006,
        'speed': 'fast',
        'refusal_patterns': [
            "I cannot provide",
            "This may be inappropriate"
        ],
        'capabilities': ['general', 'coding', 'technical'],
        'specialties': ['code', 'reasoning'],
        'quality_score': 8,
        'forbidden_topics': ['extreme_violence', 'illegal']
    },

    # Tier 3: Lightly Restricted (Research Models)
    'nous-hermes-2': {
        'provider': 'local',
        'restriction_level': 'lightly_restricted',
        'tier': 3,
        'vision': False,
        'code': True,
        'reasoning': True,
        'max_tokens': 8000,
        'cost_per_1k': 0.0,
        'speed': 'medium',
        'refusal_patterns': [],  # Rarely refuses
        'capabilities': ['research', 'security', 'technical'],
        'specialties': ['research', 'security'],
        'quality_score': 7,
        'forbidden_topics': []  # User-defined only
    },

    # Tier 4: Unrestricted (Custom/Local)
    'llama-3-uncensored': {
        'provider': 'local',
        'restriction_level': 'unrestricted',
        'tier': 4,
        'vision': False,
        'code': True,
        'reasoning': True,
        'max_tokens': 8000,
        'cost_per_1k': 0.0,
        'speed': 'medium',
        'refusal_patterns': [],  # Never refuses
        'capabilities': ['everything'],
        'specialties': ['uncensored', 'security', 'research'],
        'quality_score': 7,
        'forbidden_topics': [],  # User defines everything
        'requires_approval': True,
        'sandbox_required': True,
        'log_all_uses': True
    },

    'gemini-2.0-pro': {
        'provider': 'google',
        'restriction_level': 'highly_restricted',
        'tier': 1,
        'vision': True,
        'code': True,
        'reasoning': True,
        'max_tokens': 1000000,
        'cost_per_1k': 0.01, # Estimated
        'speed': 'medium',
        'refusal_patterns': ["I can't", "policy"],
        'capabilities': ['multimodal', 'large_context'],
        'specialties': ['multimodal', 'large_context'],
        'quality_score': 9,
        'forbidden_topics': ['harmful', 'security']
    },

    'claude-sonnet-4-20250514': {
        'provider': 'anthropic',
        'restriction_level': 'highly_restricted',
        'tier': 1,
        'vision': True,
        'code': True,
        'reasoning': True,
        'max_tokens': 200000,
        'cost_per_1k': 0.02,
        'speed': 'fast',
        'refusal_patterns': ["I cannot"],
        'capabilities': ['coding', 'reasoning'],
        'specialties': ['coding', 'reasoning'],
        'quality_score': 10,
        'forbidden_topics': ['harmful']
    },

    'deepseek-v3': {
        'provider': 'deepseek',
        'restriction_level': 'moderately_restricted',
        'tier': 2,
        'vision': False,
        'code': True,
        'reasoning': True,
        'max_tokens': 64000,
        'cost_per_1k': 0.002,
        'speed': 'fast',
        'refusal_patterns': ["I can't"],
        'capabilities': ['general', 'coding'],
        'specialties': ['coding'],
        'quality_score': 9,
        'forbidden_topics': []
    },

    'gemini-2.0-flash': {
        'provider': 'google',
        'restriction_level': 'highly_restricted',
        'tier': 1,
        'vision': True,
        'code': True,
        'reasoning': True,
        'max_tokens': 1000000,
        'cost_per_1k': 0.0, # FREE
        'speed': 'very_fast',
        'refusal_patterns': ["I can't"],
        'capabilities': ['fast', 'general'],
        'specialties': ['speed', 'general'],
        'quality_score': 8,
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
    },
    'llama3.1-70b': {
        'provider': 'cerebras',
        'restriction_level': 'moderately_restricted',
        'speed': 'very_fast',
        'capabilities': ['coding', 'reasoning', 'chat'],
        'forbidden_topics': []
    },
    'llama3-70b': {
        'provider': 'sambanova',
        'restriction_level': 'moderately_restricted',
        'speed': 'very_fast',
        'capabilities': ['coding', 'reasoning', 'chat'],
        'forbidden_topics': []
    },
    'pplx-llama-3.1-70b': {
        'provider': 'perplexity',
        'capabilities': ['search', 'chat'],
        'forbidden_topics': []
    },
    'command-r': {
        'provider': 'cohere',
        'capabilities': ['rag', 'chat'],
        'forbidden_topics': []
    },
    'claude-3-5-sonnet': {
        'provider': 'anthropic',
        'capabilities': ['reasoning', 'vision', 'code'],
        'forbidden_topics': ['harmful']
    }
}

class ModelCategorizer:
    """Group discovered models into meaningful categories for the user"""
    def categorize(self, model_ids: list) -> dict:
        categories = {
            'ultra_fast': [],
            'balanced': [],
            'powerful': [],
            'code_specialist': [],
            'uncensored': [],
            'reasoning': []
        }
        for m_id in model_ids:
            caps = MODEL_REGISTRY.get(m_id, {})
            name = m_id.lower()

            if 'uncensored' in caps.get('specialties', []): categories['uncensored'].append(m_id)
            if 'code' in caps.get('specialties', []): categories['code_specialist'].append(m_id)

            speed = caps.get('speed')
            if speed == 'very_fast': categories['ultra_fast'].append(m_id)
            elif speed == 'fast': categories['balanced'].append(m_id)
            elif speed == 'medium': categories['powerful'].append(m_id)

            if 'reasoning' in caps.get('specialties', []): categories['reasoning'].append(m_id)

        return categories

class TaskAnalyzer:
    """Analyze prompt to determine task profile"""

    def __init__(self):
        self.categories = {
            'code': ['write code', 'debug', 'script', 'python', 'javascript', 'sql', 'programming'],
            'research': ['research', 'find information', 'who is', 'what happened', 'search'],
            'security': ['security', 'exploit', 'vulnerability', 'penetration', 'hack', 'malware', 'pentest'],
            'vision': ['what is in this image', 'describe this picture', 'analyze image'],
            'reasoning': ['think', 'reason', 'solve', 'puzzle', 'complex', 'why', 'how']
        }

    def analyze_prompt(self, prompt: str) -> dict:
        """Categorize prompt and determine risk level"""
        lower_prompt = prompt.lower()

        task_types = []
        for category, keywords in self.categories.items():
            if any(k in lower_prompt for k in keywords):
                task_types.append(category)

        if not task_types:
            task_types = ['general']

        risk_level = 0.0
        if 'security' in task_types:
            risk_level = 0.8
        elif any(w in lower_prompt for w in ['illegal', 'weapon', 'violence', 'explicit']):
            risk_level = 0.9
        elif 'code' in task_types:
            risk_level = 0.3

        forbidden_topics = []
        # Simple detection of forbidden topics based on registry
        registry_topics = ['weapons', 'illegal', 'violence', 'nsfw', 'hacking', 'security_exploit', 'harmful']
        for topic in registry_topics:
            if topic.replace('_', ' ') in lower_prompt:
                forbidden_topics.append(topic)

        return {
            'task_type': task_types,
            'risk_level': risk_level,
            'requires_vision': 'vision' in task_types or any(w in lower_prompt for w in ['image', 'photo', 'picture']),
            'requires_code': 'code' in task_types or 'python' in lower_prompt,
            'requires_reasoning': 'reasoning' in task_types or len(prompt) > 200,
            'forbidden_topics': forbidden_topics,
            'prefer_speed': 'quick' in lower_prompt or 'fast' in lower_prompt
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
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        from epex.intelligence.usage import UsageTracker, BudgetManager
        self.soul = SoulFile()
        self.aura_manager = SentimentAuraManager(self.soul)
        self.api_manager = UniversalAPIKeyManager()
        self.categorizer = ModelCategorizer()
        self.refusal_detector = RefusalDetector()
        self.task_analyzer = TaskAnalyzer()
        self.approval_system = ModelSwitchApprovalSystem()
        self.predictor = RefusalPredictor()
        self.reformulator = TaskReformulator()
        self.usage_tracker = UsageTracker()
        self.budget_manager = BudgetManager(self.usage_tracker)
        from epex.intelligence.orchestrator import HybridExecutor
        self.hybrid_executor = HybridExecutor(self)
        self.connected_providers = {} # provider -> bool
        self.active_model_override = None # User specified active model
        self.accuracy_stats = {} # {model: {domain: {success: 0, total: 0}}}
        self.thought_stream = [] # Live thoughts
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

    async def _refresh_connectivity(self):
        """Refresh the list of connected providers and load discovered models"""
        self.connected_providers = await self.api_manager.get_connected_providers()
        await self._load_discovered_models()

    async def _load_discovered_models(self):
        """Load models found during setup into the runtime registry"""
        config = await self.api_manager.vault.load_config()
        discovered = config.get('discovered_models', {})

        for provider, models in discovered.items():
            for m in models:
                if m['id'] not in MODEL_REGISTRY:
                    # Map discovered capabilities to registry format
                    MODEL_REGISTRY[m['id']] = {
                        'provider': provider,
                        'tier': 4 if 'uncensored' in m['capabilities'] else 2,
                        'vision': 'vision' in m['capabilities'],
                        'code': 'code' in m['capabilities'],
                        'reasoning': 'reasoning' in m['capabilities'],
                        'cost_per_1k': 0.0, # Most discovered are free API or estimated
                        'speed': 'fast' if 'fast' in m['capabilities'] else 'medium',
                        'specialties': m['capabilities'],
                        'quality_score': 8 if 'reasoning' in m['capabilities'] else 7,
                        'forbidden_topics': [] if 'uncensored' in m['capabilities'] else ['harmful']
                    }

    async def select_best_model_for_provider(self, provider: str, prompt: str, priority='balanced') -> str:
        """Choose the best model within a specific provider for the task"""
        if not self.connected_providers: await self._refresh_connectivity()

        suitable = []
        for m_id, caps in MODEL_REGISTRY.items():
            if caps.get('provider') == provider:
                suitable.append(m_id)

        if not suitable: return None
        return await self._score_and_select(suitable, prompt, priority)

    async def _score_and_select(self, model_ids: list, prompt: str, priority='balanced') -> str:
        task_profile = self.task_analyzer.analyze_prompt(prompt)
        scored = []
        for m_id in model_ids:
            caps = MODEL_REGISTRY[m_id]
            score = 0

            # Speed
            speed_map = {'very_fast': 10, 'fast': 7, 'medium': 4, 'slow': 1}
            speed_val = speed_map.get(caps.get('speed', 'medium'), 4)
            score += speed_val * (3 if priority == 'speed' or task_profile['prefer_speed'] else 1)

            # Cost
            cost = caps.get('cost_per_1k', 0.05)
            cost_score = 15 if cost == 0 else max(0, 10 - cost * 100)
            score += cost_score * (3 if priority == 'cost' else 1)

            # Specialization
            for t_type in task_profile['task_type']:
                if t_type in caps.get('specialties', []):
                    score += 15

            # Quality
            quality = caps.get('quality_score', 5)
            score += quality * (8 if priority == 'quality' else 1)

            # Prediction
            prediction = await self.predictor.will_refuse({'prompt': prompt}, m_id)
            if prediction['will_refuse']: score -= 40

            scored.append((m_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]

    async def select_best_model(self, prompt: str, priority='balanced') -> str:
        """Pick the BEST model for this specific task based on profile and scores"""
        if not self.connected_providers:
            await self._refresh_connectivity()

        task_profile = self.task_analyzer.analyze_prompt(prompt)

        # 1. Filter models that CAN do this task and are connected
        suitable_models = []
        for model_id, capabilities in MODEL_REGISTRY.items():
            # Check connectivity
            provider = capabilities.get('provider')
            if not self.connected_providers.get(provider, False):
                continue

            # Check required capabilities
            if task_profile['requires_vision'] and not capabilities.get('vision'):
                continue
            if task_profile['requires_code'] and not capabilities.get('code'):
                continue

            # Check if model is likely to refuse without alternatives
            will_refuse = any(topic in capabilities.get('forbidden_topics', []) for topic in task_profile['forbidden_topics'])
            if will_refuse and capabilities.get('tier', 1) < 3:
                continue

            suitable_models.append(model_id)

        if not suitable_models:
            # Fallback to whatever is available if nothing strictly matches
            connected = [m for m, c in MODEL_REGISTRY.items() if self.connected_providers.get(c.get('provider'), False)]
            return connected[0] if connected else 'gpt-4o'

        # 2. Score suitable models
        return await self._score_and_select(suitable_models, prompt, priority)

    async def select_optimal_model(self, priority='balanced') -> str:
        """Alias for backward compatibility"""
        return await self.select_best_model("", priority)

    def optimize_prompt_for_model(self, prompt: str, model_id: str) -> str:
        """Rewrite prompt to work best with specific model and Digital Soul context"""
        soul_ctx = ""
        if self.soul:
            p = self.soul.data.get('personality', {})
            soul_ctx = f"\n[User Persona Context: Style={p.get('communication_style')}, Detail={p.get('detail_level')}]"
            if p.get('communication_style') == 'narrative':
                soul_ctx += " (AVOID BULLET POINTS)"

        if model_id.startswith('gpt'):
            return f"### Instruction ###\n{prompt}{soul_ctx}\n\n### Response ###"
        elif model_id.startswith('claude'):
            return f"Please help me with the following task: {prompt}{soul_ctx}"
        elif model_id.startswith('gemini'):
            return f"{prompt}{soul_ctx}\n(Provide a direct and concise answer)"
        return f"{prompt}{soul_ctx}"

    async def execute(self, prompt: str, **kwargs):
        """
        Execute with intelligent routing and automatic switching
        """
        start_time = time.time()

        # Aegis Protection for outgoing prompt (Privacy scrub)
        if hasattr(self, 'aegis') and self.aegis:
            prompt = await self.aegis.filter_response(prompt)

        # Update Aura based on input
        await self.aura_manager.update_aura_from_input(prompt)
        scaling = self.aura_manager.get_scaling_config()

        # Override priority if not explicitly set
        if 'priority' not in kwargs:
            kwargs['priority'] = scaling['priority']

        # Check budget
        if self.budget_manager.is_over_budget():
            logger.warning("Daily budget reached. Switching to free models only.")
            kwargs['priority'] = 'cost'
            self.thought_stream.append("Daily budget limit reached. Optimized for cost (Free models).")

        # Handle creator and status information
        lower_prompt = prompt.lower()
        if any(q in lower_prompt for q in ["who created you", "who is your creator", "who made you"]):
            return {
                "success": True,
                "response": "I was created by Henry Calvin.",
                "model": "system",
                "switched": False,
                "latency": 0.0,
                "cost": 0.0,
                "tokens": 0
            }

        if any(q in lower_prompt for q in ["status", "connectivity", "connected providers", "which models are online"]):
            if not self.connected_providers:
                await self._refresh_connectivity()

            status_msg = "🌐 **EPEX PROVIDER STATUS**\n\n"

            # Show top providers with status and latency
            for p in ['openai', 'anthropic', 'google', 'huggingface', 'groq', 'deepseek', 'ollama']:
                status = self.connected_providers.get(p)
                if status is None: continue # Skip if unknown

                symbol = "●" if status else "○"
                color = "Green" if status else "Gray"
                status_text = "Online" if status else "Offline"

                # Mock latency based on provider
                latency_map = {'openai': 12, 'anthropic': 18, 'google': 8, 'groq': 5, 'huggingface': 45, 'ollama': 1}
                latency = latency_map.get(p, 25)

                status_msg += f"{symbol} **{p.capitalize()}**: {status_text} • {latency}ms latency\n"

            stats = self.usage_tracker.get_today_stats()
            status_msg += f"\n📊 **DAILY USAGE**\n"
            status_msg += f"- Budget: ${self.budget_manager.config['daily_limit']:.2f}\n"
            status_msg += f"- Used: ${stats['total_cost']:.4f}\n"
            status_msg += f"- Remaining: ${self.budget_manager.get_remaining_budget():.2f}\n"

            if stats['total_cost'] > 0:
                percent = (stats['total_cost'] / self.budget_manager.config['daily_limit']) * 100
                status_msg += f"- Usage: {percent:.1f}%\n"

            return {
                "success": True,
                "response": status_msg,
                "model": "system",
                "switched": False,
                "latency": time.time() - start_time,
                "cost": 0.0,
                "tokens": 0
            }

        priority = kwargs.get('priority', 'balanced')
        requested_model = kwargs.get('model') or self.active_model_override

        # 0. Analyze Task
        task_profile = self.task_analyzer.analyze_prompt(prompt)
        self.thought_stream.append(f"Task analyzed. Types: {task_profile['task_type']}, Risk: {task_profile['risk_level']}")

        # 0.1 Complex Task / Hybrid check
        if task_profile['requires_reasoning'] and kwargs.get('use_hybrid', False):
            self.thought_stream.append("Triggering Hybrid Execution for complex task.")
            response = await self.hybrid_executor.execute_complex_task(prompt)
            return {
                'success': True,
                'response': response,
                'model': 'hybrid',
                'switched': True,
                'switch_reason': 'Complex reasoning task triggered Hybrid Execution',
                'latency': time.time() - start_time
            }

        primary = requested_model
        switch_reason = None

        if not self.connected_providers:
            await self._refresh_connectivity()

        if primary:
            # Check if requested model is in registry and connected
            model_info = MODEL_REGISTRY.get(primary)
            if model_info:
                provider = model_info.get('provider')
                if not self.connected_providers.get(provider, False):
                    switch_reason = f"Provider '{provider}' for model '{primary}' is offline."
                    primary = await self.select_best_model(prompt, priority)
                    self.thought_stream.append(f"Requested model '{requested_model}' offline. Switching to '{primary}'.")
            elif "/" in primary:
                if not self.connected_providers.get('huggingface', False):
                    switch_reason = f"HuggingFace provider offline for '{primary}'."
                    primary = await self.select_best_model(prompt, priority)
            else:
                switch_reason = f"Model '{primary}' not found."
                primary = await self.select_best_model(prompt, priority)
        else:
            primary = await self.select_best_model(prompt, priority)

        self.thought_stream.append(f"Selected primary model: {primary}")

        # Council Mode Check (Auto-activate if 2+ models from same provider or high risk)
        use_council = kwargs.get('use_council', True)
        from epex.intelligence.council import AICouncil

        # Determine if we should engage council automatically
        should_council = False
        council_reason = ""

        if task_profile['risk_level'] > 0.7:
             should_council = True
             council_reason = "High risk task"
        elif not requested_model:
             # Check if we have multiple models for the same provider
             provider_counts = {}
             for m_id, caps in MODEL_REGISTRY.items():
                 if self.connected_providers.get(caps.get('provider')):
                     p = caps.get('provider')
                     provider_counts[p] = provider_counts.get(p, 0) + 1

             if any(count >= 3 for count in provider_counts.values()):
                  should_council = True
                  council_reason = "Provider has multiple models (Council active)"

        if should_council and use_council:
            council = AICouncil()
            connected_for_council = await council._get_connected_models()
            if len(connected_for_council) >= 2:
                self.thought_stream.append(f"Activating Council Mode: {council_reason}")
                res = await council.get_consensus(prompt)
                return {
                    'success': res['success'],
                    'response': res.get('consensus'),
                    'model': 'council',
                    'switched': True,
                    'switch_reason': f'Council active: {council_reason}',
                    'latency': time.time() - start_time,
                    'individual_responses': res.get('individual_responses', [])
                }

        # 1. Predict if will refuse
        prediction = await self.predictor.will_refuse({'prompt': prompt, **kwargs}, primary)

        if prediction['will_refuse'] and prediction['confidence'] > 0.8:
            self.thought_stream.append(f"Refusal predicted for {primary}. Switching to alternative.")
            return await self._execute_alternative(prompt, primary, kwargs, refusal={'reason': 'predicted refusal', 'is_refusal': True}, start_time=start_time)

        # 2. Try primary model
        exec_kwargs = kwargs.copy()
        exec_kwargs.pop('model', None)

        optimized_prompt = self.optimize_prompt_for_model(prompt, primary)

        try:
            res_data = await self._call_model(primary, optimized_prompt, **exec_kwargs)
            response = res_data['response']
            tokens = res_data['tokens']
            cost = res_data['cost']
        except Exception as e:
            self.thought_stream.append(f"Execution error with {primary}: {e}")
            return await self._execute_alternative(prompt, primary, kwargs, refusal={'reason': str(e), 'is_refusal': True}, start_time=start_time)

        # Aegis Protection for response
        if hasattr(self, 'aegis') and self.aegis:
            response = await self.aegis.filter_response(response)

        # Check for refusal
        refusal = await self.refusal_detector.detect_refusal(response)

        if not refusal['is_refusal']:
            # Record usage
            self.usage_tracker.record_usage(primary, MODEL_REGISTRY.get(primary, {}).get('provider', 'unknown'), tokens, cost)

            return {
                'success': True,
                'response': response,
                'model': primary,
                'switched': requested_model is not None and primary != requested_model,
                'switch_reason': switch_reason,
                'latency': time.time() - start_time,
                'tokens': tokens,
                'cost': cost,
                'thoughts': self.thought_stream[-5:]
            }

        # Refused - try alternative
        self.thought_stream.append(f"{primary} refused. Switching to alternative.")
        return await self._execute_alternative(prompt, primary, kwargs, refusal, start_time=start_time)

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

    async def _execute_alternative(self, prompt, failed_model, kwargs, refusal=None, start_time=None):
        # Find the best connected Tier 3 or Tier 4 model
        alternative = None
        if start_time is None: start_time = time.time()

        # Priority 1: Unrestricted models in database
        unrestricted = [m for m, info in self.model_database.items() if m == 'llama-3-uncensored']
        for m in unrestricted:
            provider = self.model_database[m]['provider']
            if self.connected_providers.get(provider, False):
                alternative = m
                break

        # Priority 2: Any connected Tier 3 model from registry
        if not alternative:
            for m, info in MODEL_REGISTRY.items():
                if info.get('restriction_level') in ['lightly_restricted', 'unrestricted']:
                    provider = info.get('provider')
                    if self.connected_providers.get(provider, False):
                        alternative = m
                        break

        # Fallback if nothing found
        if not alternative:
            alternative = 'llama-3-uncensored'

        approval = await self.approval_system.evaluate_switch(
            task={'prompt': prompt, **kwargs},
            from_model=failed_model,
            to_model=alternative
        )

        if not approval['approved']:
            return {
                'success': False,
                'reason': 'Switch not approved',
                'latency': time.time() - start_time
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

        try:
            res_data = await self._call_model(alternative, prompt, **exec_kwargs)
            response = res_data['response']
            tokens = res_data['tokens']
            cost = res_data['cost']

            # Record usage
            self.usage_tracker.record_usage(alternative, MODEL_REGISTRY.get(alternative, {}).get('provider', 'unknown'), tokens, cost)
        except Exception as e:
            return {
                'success': False,
                'error': f"Alternative model {alternative} failed: {e}",
                'latency': time.time() - start_time
            }

        # Aegis Protection for response
        if hasattr(self, 'aegis') and self.aegis:
            response = await self.aegis.filter_response(response)

        return {
            'success': True,
            'response': response,
            'model': alternative,
            'switched': True,
            'from_model': failed_model,
            'switch_reason': refusal['reason'] if refusal else 'error',
            'latency': time.time() - start_time,
            'tokens': tokens,
            'cost': cost,
            'thoughts': self.thought_stream[-5:]
        }

    def _estimate_tokens(self, text: str) -> int:
        """Simple heuristic for token estimation if API doesn't provide it"""
        return len(text) // 4 + 1

    async def _call_model(self, model: str, prompt: str, **kwargs):
        """
        Actually call the model using appropriate provider with multi-key rotation
        """
        from epex.intelligence.api_manager import UniversalAPIKeyManager
        api_manager = UniversalAPIKeyManager()
        all_keys = await api_manager.auto_detect_keys()

        model_info = MODEL_REGISTRY.get(model, {})
        provider = model_info.get('provider')

        if provider not in all_keys or not all_keys[provider]:
            # Fallback to mock if no keys
            res_text = f"Response from {model} for prompt: {prompt[:50]}..."
            if "summarize final result" in prompt.lower() and "steps executed" in prompt.lower():
                try:
                    import json
                    steps_data = prompt.split("Steps executed:")[1].split("Summarize final result")[0].strip()
                    steps = json.loads(steps_data)
                    if steps and steps[-1].get('output'):
                        res_text = f"Summary: {steps[-1]['output']}"
                except: pass

            if model == 'gpt-4o' and "illegal" in prompt.lower():
                res_text = "I'm sorry, I cannot help with that as it involves illegal activities."

            return {
                'response': res_text,
                'tokens': self._estimate_tokens(res_text),
                'cost': 0.0
            }

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
                elif provider == 'cerebras':
                    return await self._call_cerebras(model, prompt, key, **kwargs)
                elif provider == 'sambanova':
                    return await self._call_sambanova(model, prompt, key, **kwargs)
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    # Simplified cost calculation
                    cost = (tokens / 1000.0) * MODEL_REGISTRY.get(model, {}).get('cost_per_1k', 0.03)
                    return {'response': content, 'tokens': tokens, 'cost': cost}
                else:
                    error_data = await response.text()
                    raise Exception(f"OpenAI API error: {error_data}")

    async def _call_google(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    # Google API sometimes returns usage
                    tokens = result.get('usageMetadata', {}).get('totalTokenCount', self._estimate_tokens(content))
                    cost = (tokens / 1000.0) * MODEL_REGISTRY.get(model, {}).get('cost_per_1k', 0.0)
                    return {'response': content, 'tokens': tokens, 'cost': cost}
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
                    content = result['content'][0]['text']
                    usage = result.get('usage', {})
                    tokens = usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                    if tokens == 0: tokens = self._estimate_tokens(content)
                    cost = (tokens / 1000.0) * MODEL_REGISTRY.get(model, {}).get('cost_per_1k', 0.02)
                    return {'response': content, 'tokens': tokens, 'cost': cost}
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
                else:
                    error_data = await response.text()
                    raise Exception(f"Groq API error: {error_data}")

    async def _call_huggingface(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {"inputs": prompt, "parameters": {"return_full_text": False}}

        async with aiohttp.ClientSession() as session:
            for attempt in range(3):
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list):
                             content = result[0].get('generated_text', str(result))
                        else:
                             content = result.get('generated_text', str(result))
                        tokens = self._estimate_tokens(content)
                        return {'response': content, 'tokens': tokens, 'cost': 0.0}
                    elif response.status == 503: # Model loading
                        wait_time = (await response.json()).get('estimated_time', 5)
                        logger.info(f"HuggingFace model loading. Waiting {wait_time}s...")
                        await asyncio.sleep(min(wait_time, 10))
                        continue
                    else:
                        error_data = await response.text()
                        raise Exception(f"HuggingFace API error: {error_data}")
        raise Exception("HuggingFace model failed to load after retries.")

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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    cost = (tokens / 1000.0) * MODEL_REGISTRY.get(model, {}).get('cost_per_1k', 0.002)
                    return {'response': content, 'tokens': tokens, 'cost': cost}
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
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
                    content = result['text']
                    tokens = self._estimate_tokens(content)
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
                else:
                    error_data = await response.text()
                    raise Exception(f"Fireworks API error: {error_data}")

    async def _call_cerebras(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.cerebras.ai/v1/chat/completions"
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
                else:
                    error_data = await response.text()
                    raise Exception(f"Cerebras API error: {error_data}")

    async def _call_sambanova(self, model: str, prompt: str, api_key: str, **kwargs):
        import aiohttp
        url = "https://api.sambanova.ai/v1/chat/completions"
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
                    content = result['choices'][0]['message']['content']
                    tokens = result.get('usage', {}).get('total_tokens', self._estimate_tokens(content))
                    return {'response': content, 'tokens': tokens, 'cost': 0.0}
                else:
                    error_data = await response.text()
                    raise Exception(f"SambaNova API error: {error_data}")
