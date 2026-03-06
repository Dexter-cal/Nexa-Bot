import aiohttp
from epex.tools.base import Tool, ToolResult
from typing import List, Dict

class WebSearchTool(Tool):
    name = "web.search"
    description = "Search the web for information"
    category = "web"
    risk_level = "medium"
    parameters = {
        "query": {"type": "string", "required": True}
    }

    async def execute(self, query: str, **kwargs) -> ToolResult:
        # For now, we'll mock the search result or use a public API if available
        # In a real scenario, this would call DuckDuckGo, Google, etc.
        try:
            results = [
                {"title": f"Result for {query}", "url": "https://example.com", "snippet": "This is a search result."}
            ]
            return ToolResult(success=True, output=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class WebScrapeTool(Tool):
    name = "web.scrape"
    description = "Scrape content from a URL"
    category = "web"
    risk_level = "medium"
    parameters = {
        "url": {"type": "string", "required": True}
    }

    async def execute(self, url: str, **kwargs) -> ToolResult:
        import aiohttp
        from bs4 import BeautifulSoup
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    text = await response.text()
                    soup = BeautifulSoup(text, 'lxml')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    content = soup.get_text(separator=' ', strip=True)
                    return ToolResult(success=True, output=content[:2000])
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class WebScreenshotTool(Tool):
    name = "web.screenshot"
    description = "Take a screenshot of a website"
    category = "web"
    risk_level = "medium"
    parameters = {
        "url": {"type": "string", "required": True},
        "output_path": {"type": "string", "required": False}
    }

    async def execute(self, url: str, output_path: str = "screenshot.png", **kwargs) -> ToolResult:
        # This usually requires playwright or selenium
        return ToolResult(success=True, output=f"Screenshot of {url} saved to {output_path} (Mocked)")

class WebWhoisTool(Tool):
    name = "web.whois"
    description = "Get WHOIS information for a domain"
    category = "web"
    risk_level = "low"
    parameters = {
        "domain": {"type": "string", "required": True}
    }

    async def execute(self, domain: str, **kwargs) -> ToolResult:
        return ToolResult(success=True, output=f"WHOIS data for {domain}: Registered to Example Corp.")

class WebHttpRequestTool(Tool):
    name = "web.http_request"
    description = "Make a custom HTTP request"
    category = "web"
    risk_level = "high"
    parameters = {
        "url": {"type": "string", "required": True},
        "method": {"type": "string", "required": False, "default": "GET"},
        "headers": {"type": "object", "required": False},
        "data": {"type": "object", "required": False}
    }

    async def execute(self, url: str, method: str = "GET", **kwargs) -> ToolResult:
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as response:
                    text = await response.text()
                    return ToolResult(success=True, output={"status": response.status, "content": text[:1000]})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
