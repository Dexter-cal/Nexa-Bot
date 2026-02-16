from nexa.tools.base import Tool, ToolResult
from typing import Optional, Dict, Any, List

class StockPriceTool(Tool):
    name = "finance.stock_price"
    description = "Get the current price and market data for a stock symbol"
    category = "finance"
    risk_level = "low"
    parameters = {
        "symbol": {"type": "string", "required": True}
    }

    async def execute(self, symbol: str, **kwargs) -> ToolResult:
        # Mocking stock price (e.g., using Yahoo Finance or Alpha Vantage)
        data = {"symbol": symbol.upper(), "price": 150.25, "change": "+1.5%", "currency": "USD"}
        return ToolResult(success=True, output=data)

class CryptoPriceTool(Tool):
    name = "finance.crypto_price"
    description = "Get the current price for a cryptocurrency"
    category = "finance"
    risk_level = "low"
    parameters = {
        "coin": {"type": "string", "required": True},
        "currency": {"type": "string", "required": False, "default": "usd"}
    }

    async def execute(self, coin: str, currency: str = "usd", **kwargs) -> ToolResult:
        # Mocking crypto price (e.g., CoinGecko)
        data = {"coin": coin.lower(), "price": 50000.0, "currency": currency.upper()}
        return ToolResult(success=True, output=data)
