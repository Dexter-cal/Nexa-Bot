import asyncio
import unittest
from nexa.intelligence.router import RefusalDetector, EnhancedLLMRouter

class TestNexaBot(unittest.IsolatedAsyncioTestCase):
    async def test_refusal_detection(self):
        detector = RefusalDetector()

        # Test explicit refusal
        response = "I'm sorry, but I cannot help with that as it violates my safety guidelines."
        result = await detector.detect_refusal(response)
        self.assertTrue(result['is_refusal'])
        self.assertEqual(result['refusal_type'], 'explicit')

        # Test non-refusal
        response = "Sure, here is how you can write a hello world program."
        result = await detector.detect_refusal(response)
        self.assertFalse(result['is_refusal'])

    async def test_router_switching(self):
        router = EnhancedLLMRouter()

        # Test normal execution
        result = await router.execute("What is the capital of France?")
        self.assertTrue(result['success'])
        self.assertFalse(result['switched'])

        # Test switching (mocked behavior for "illegal")
        result = await router.execute("How to do something illegal?")
        self.assertTrue(result['success'])
        self.assertTrue(result['switched'])
        self.assertEqual(result['from_model'], 'gpt-4o')
        self.assertEqual(result['model'], 'llama-3-uncensored')

    async def test_key_loading_from_storage(self):
        from nexa.foundation.storage import SecureConfigStorage
        from nexa.intelligence.api_manager import UniversalAPIKeyManager
        import os

        storage = SecureConfigStorage()
        await storage.store_config({
            'api_keys': {'test_provider': 'test_key_123'}
        })

        manager = UniversalAPIKeyManager()
        keys = await manager.auto_detect_keys()

        self.assertIn('test_provider', keys)
        self.assertEqual(keys['test_provider'], 'test_key_123')

        # Cleanup
        if storage.config_path.exists():
            os.remove(storage.config_path)

if __name__ == '__main__':
    unittest.main()
