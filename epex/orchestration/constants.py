MODES = {
    'assistive': {
        'description': 'Helpful but passive - only acts when asked',
        'autonomy_level': 1,
        'initiative': False,
        'approval_required': True,
        'proactive_suggestions': False,
    },
    'partner': {
        'description': 'Proactive collaborator - suggests and helps plan',
        'autonomy_level': 5,
        'initiative': True,
        'approval_required': True,
        'proactive_suggestions': True,
    },
    'autonomous': {
        'description': 'Fully independent - acts within guardrails',
        'autonomy_level': 9,
        'initiative': True,
        'approval_required': False,
        'proactive_suggestions': True,
        'self_directed': True,
    },
    'shadow': {
        'description': 'Observes and learns but never acts',
        'autonomy_level': 0,
        'initiative': False,
        'approval_required': True,
        'observation_only': True,
    },
    'collaborative': {
        'description': 'Works alongside you in real-time',
        'autonomy_level': 6,
        'initiative': True,
        'approval_required': False,
        'real_time_sync': True,
    }
}

ROLES = {
    'hacker': {
        'personality': 'Security researcher, ethical hacker',
        'expertise': ['pentesting', 'exploit_development', 'security_analysis'],
        'tools_enabled': ['network.portscan', 'security.check_vuln'],
        'model_preference': 'llama-3-uncensored',
        'tone': 'technical, direct, security-focused',
    },
    'developer': {
        'personality': 'Software engineer, problem solver',
        'expertise': ['coding', 'debugging', 'architecture', 'testing'],
        'tools_enabled': ['dev.generate_code', 'dev.review_code'],
        'model_preference': 'gpt-4o',
        'tone': 'pragmatic, clean code focused',
    },
    'researcher': {
        'personality': 'Academic researcher, analyst',
        'expertise': ['research', 'analysis', 'synthesis', 'citation'],
        'tools_enabled': ['web.search', 'learn.research_topic'],
        'model_preference': 'claude-sonnet-4',
        'tone': 'academic, thorough, evidence-based',
    },
    'assistant': {
        'personality': 'General purpose helper',
        'expertise': ['general', 'adaptable'],
        'tools_enabled': 'all',
        'model_preference': 'gpt-4o',
        'tone': 'friendly, helpful',
    }
}
