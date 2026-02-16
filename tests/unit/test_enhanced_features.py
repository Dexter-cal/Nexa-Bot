import pytest
from nexa.tools.multimedia import ImageResizeTool
from nexa.tools.productivity import NoteTakingTool
from nexa.tools.network import DNSLookupTool
from nexa.intelligence.router import EnhancedLLMRouter
from nexa.orchestration.teach_mode import TeachMode
import os

class TestEnhancedFeatures:
    @pytest.mark.asyncio
    async def test_multimedia_tool_resize(self):
        # We need a dummy image to test
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save('test.png')

        tool = ImageResizeTool()
        result = await tool.execute(path='test.png', width=50, height=50, output_path='test_resized.png')
        assert result.success is True
        assert os.path.exists('test_resized.png')

        # Cleanup
        os.remove('test.png')
        os.remove('test_resized.png')

    @pytest.mark.asyncio
    async def test_productivity_tool_note(self):
        tool = NoteTakingTool()
        result = await tool.execute(title='test_note', content='Hello Nexa!')
        assert result.success is True
        assert os.path.exists('notes/test_note.txt')

        # Cleanup
        os.remove('notes/test_note.txt')

    @pytest.mark.asyncio
    async def test_network_tool_dns(self):
        tool = DNSLookupTool()
        result = await tool.execute(domain='google.com')
        assert result.success is True
        assert len(result.output) > 0

    @pytest.mark.asyncio
    async def test_router_optimization(self):
        router = EnhancedLLMRouter()
        model = await router.select_optimal_model(priority='cost')
        assert model == 'llama-3-uncensored' # Based on my scores

        model = await router.select_optimal_model(priority='quality')
        assert model == 'gpt-4o'

    @pytest.mark.asyncio
    async def test_teach_mode(self):
        tm = TeachMode()
        await tm.start_recording("test_wf")
        tm.record_action("click", "submit_button")
        tm.record_action("type", "search_bar", value="Nexa Bot")
        workflow = await tm.stop_recording()

        assert workflow['name'] == "test_wf"
        assert len(workflow['steps']) == 2
        assert workflow['steps'][0]['action_type'] == "click"
