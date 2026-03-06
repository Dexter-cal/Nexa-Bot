import logging
import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from epex.tools.base import Tool, ToolResult

logger = logging.getLogger(__name__)

class InternetInteractorTool(Tool):
    name = "web.interactor"
    description = "Advanced tool for interacting with the internet, browsing, and form detection."
    category = "web"
    risk_level = "medium"
    parameters = {
        "action": {"type": "string", "required": True}, # browse, find_forms, submit_form
        "url": {"type": "string", "required": True},
        "data": {"type": "object", "required": False}
    }

    async def execute(self, action: str, url: str, data: Dict[str, Any] = None, **kwargs) -> ToolResult:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                if action == "browse":
                    response = await client.get(url)
                    soup = BeautifulSoup(response.text, 'lxml')
                    text = soup.get_text(separator=' ', strip=True)[:2000]
                    return ToolResult(success=True, output={"content": text, "url": str(response.url)})

                elif action == "find_forms":
                    response = await client.get(url)
                    soup = BeautifulSoup(response.text, 'lxml')
                    forms = []
                    for i, form in enumerate(soup.find_all('form')):
                        inputs = []
                        for inp in form.find_all(['input', 'select', 'textarea']):
                            inputs.append({
                                "name": inp.get('name'),
                                "type": inp.get('type', 'text'),
                                "id": inp.get('id')
                            })
                        forms.append({
                            "index": i,
                            "action": form.get('action'),
                            "method": form.get('method', 'get').upper(),
                            "inputs": inputs
                        })
                    return ToolResult(success=True, output={"forms": forms})

                elif action == "submit_form":
                    method = (data or {}).get('method', 'POST').upper()
                    form_data = (data or {}).get('fields', {})
                    if method == 'POST':
                        response = await client.post(url, data=form_data)
                    else:
                        response = await client.get(url, params=form_data)
                    return ToolResult(success=True, output={"response_code": response.status_code, "final_url": str(response.url)})

            return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class AccountCreatorTool(Tool):
    name = "automation.account_creator"
    description = "Assists in signing up for platforms by detecting registration flows."
    category = "automation"
    risk_level = "high"
    parameters = {
        "platform": {"type": "string", "required": True},
        "user_info": {"type": "object", "required": True}
    }

    async def execute(self, platform: str, user_info: Dict[str, Any], **kwargs) -> ToolResult:
        logger.info(f"Initiating account creation for {platform}")

        urls = {
            "github": "https://github.com/signup",
            "google": "https://accounts.google.com/signup",
            "twitter": "https://twitter.com/i/flow/signup",
            "discord": "https://discord.com/register",
            "telegram": "https://web.telegram.org/a/#/login"
        }

        url = urls.get(platform.lower())
        if not url:
            return ToolResult(success=False, error=f"Platform {platform} not supported for auto-signup yet.")

        return ToolResult(
            success=True,
            output={
                "status": "pending",
                "message": f"Assisting with {platform} signup. Navigate to {url}. I can provide these details: {list(user_info.keys())}",
                "registration_url": url
            }
        )
