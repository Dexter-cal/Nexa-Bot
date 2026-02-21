import sys
import asyncio
import argparse
from epex.interfaces.tui import TUISetupWizard
from epex.core.engine import engine

async def async_main():
    parser = argparse.ArgumentParser(description="Epex Bot CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt for Epex Bot")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--mode", help="Set operational mode")
    parser.add_argument("--role", help="Set agent role")
    parser.add_argument("--spawn", help="Spawn a specialized agent with role")
    parser.add_argument("--chat", action="store_true", help="Start interactive neural chat")
    parser.add_argument("--visuals", action="store_true", help="Display visual mockups of Epex interfaces")
    parser.add_argument("--quick-setup", action="store_true", help="Fast-track setup with automatic defaults")
    parser.add_argument("--key", nargs=2, metavar=('PROVIDER', 'VALUE'), help="Quickly set an API key (e.g. --key openai sk-...)")
    parser.add_argument("--connect", nargs=3, metavar=('NAME', 'URL', 'KEY'), help="Connect to another Epex instance")
    parser.add_argument("--peers", action="store_true", help="List all connected Epex peers")
    parser.add_argument("--voice", action="store_true", help="Activate hands-free voice command bridge")
    parser.add_argument("--tool-hub", action="store_true", help="Open the EPEX Tool Hub")

    args = parser.parse_args()

    if args.setup:
        wizard = TUISetupWizard()
        await wizard.run()
    elif args.quick_setup:
        await run_quick_setup()
    elif args.key:
        await set_api_key(args.key[0], args.key[1])
    elif args.connect:
        from epex.core.network_node import network_node
        await network_node.add_peer(args.connect[0], args.connect[1], args.connect[2])
        print(f"✓ Successfully connected to peer '{args.connect[0]}'")
    elif args.peers:
        from epex.core.network_node import network_node
        await network_node.load_peers()
        if not network_node.peers:
            print("No peers connected.")
        else:
            print("\nConnected Epex Peers:")
            for p in network_node.peers:
                print(f" • {p['name']} ({p['url']}) - Status: {p['status']}")
    elif args.voice:
        print("🎙️ Activating Voice Command Bridge... (Say 'Epex' to trigger)")
        await engine.start()
        await engine.voice_bridge.start_listening_loop()
    elif args.tool_hub:
        from epex.interfaces.tool_hub import ToolHub
        hub = ToolHub()
        await hub.run()
    elif args.visuals:
        from epex.tools.visualizer import GenerateMockupsTool
        tool = GenerateMockupsTool()
        result = await tool.execute()
        print(result.output)
    elif args.chat or (not args.prompt and len(sys.argv) == 1 and not args.spawn and not args.visuals):
        await start_chat_loop()
    elif args.spawn:
        result = await engine.execute_command(f"spawn {args.spawn} agent")
        print(f"\n{result.get('message', 'Spawning...')}")
    elif args.prompt:
        result = await engine.execute_command(args.prompt)
        if result['success']:
            print(f"\n{result['response']}")
            if result.get('switched'):
                print(f"\n[Note: Switched from {result['from_model']} to {result['model']} because: {result['switch_reason']}]")
        else:
            print(f"Error: {result.get('reason', 'Unknown error')}")

async def start_chat_loop():
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.text import Text
    from epex.foundation.storage import SecureConfigStorage
    from epex.interfaces.prompt_assistant import PromptAssistant

    assistant = PromptAssistant()
    storage = SecureConfigStorage()
    config = await storage.load_config()
    user_name = config.get('user_name', 'User')
    epex_name = config.get('epex_name', 'Epex')

    console = Console()

    banner = Text(r"""
 ███████╗██████╗ ███████╗██╗  ██╗
 ██╔════╝██╔══██╗██╔════╝╚██╗██╔╝
 █████╗  ██████╔╝█████╗   ╚███╔╝
 ██╔══╝  ██╔═══╝ ██╔══╝   ██╔██╗
 ███████╗██║     ███████╗██╔╝ ██╗
 ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
 ⚡ APEX NEURAL OPERATING SYSTEM ⚡
    """, style="bold cyan")

    console.print(banner)
    console.print(Panel(f"[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]{epex_name.upper()} BOT is ready for task orchestration. Type 'exit' or 'quit' to end session.[/]", border_style="sky_blue1"))

    while True:
        try:
            user_input = console.input(f"\n[bold sky_blue1]{user_name} > [/]")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Intent Detection
            intent_tool = assistant.detect_intent(user_input)
            if intent_tool:
                console.print(f"[dim italic text_slate_500]Assistant: I detect you want to run {intent_tool}. Processing...[/]")

            with console.status("[bold sky_blue1]Thinking..."):
                result = await engine.execute_command(user_input)

            if result['success']:
                # Re-load config in case name changed
                config = await storage.load_config()
                user_name = config.get('user_name', 'User')
                epex_name = config.get('epex_name', 'Epex')

                console.print(f"\n[bold sky_blue1]{epex_name} >[/]")
                console.print(Markdown(result['response']))
                if result.get('switched'):
                    console.print(f"\n[dim italic text_slate_500]Note: Switched from {result['from_model']} to {result['model']} because: {result['switch_reason']}[/]")
            else:
                console.print(f"\n[bold red]Error:[/] {result.get('error', 'Unknown failure')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[bold red]System Error:[/] {e}")

async def set_api_key(provider: str, value: str):
    from rich.console import Console
    from epex.foundation.storage import SecureConfigStorage
    console = Console()
    storage = SecureConfigStorage()
    config = await storage.load_config()
    if 'api_keys' not in config: config['api_keys'] = {}
    config['api_keys'][provider.lower()] = value
    await storage.store_config(config)
    console.print(f"[bold green]✓ API Key for '{provider}' has been saved securely.[/]")

async def run_quick_setup():
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from epex.intelligence.api_manager import UniversalAPIKeyManager
    from epex.foundation.storage import SecureConfigStorage
    from epex.intelligence.defaults import SmartDefaultsEngine

    console = Console()
    console.clear()
    console.print(Panel("[bold green]⚡ EPEX EXPRESS SETUP[/]\n[white]Let's get you online in 30 seconds.[/]", border_style="green"))

    user_name = Prompt.ask("Your name", default="Max")
    bot_name = Prompt.ask("Bot name", default="Bill")

    # Quick API key entry
    console.print("\n[bold cyan]API Keys (Optional - press Enter to skip)[/]")
    openai_key = Prompt.ask("OpenAI Key", password=True, default="")
    google_key = Prompt.ask("Google/Gemini Key", password=True, default="")

    storage = SecureConfigStorage()
    defaults = SmartDefaultsEngine()

    config = await defaults.generate_config()
    config.update({
        "user_name": user_name,
        "epex_name": bot_name,
        "api_keys": {}
    })

    if openai_key: config['api_keys']['openai'] = openai_key
    if google_key: config['api_keys']['google'] = google_key

    await storage.store_config(config)

    console.print(Panel.fit(f"[bold green]✓ Express Setup Complete![/]\n[white]Welcome, {user_name}. I am {bot_name}.[/]\nRun: [bold]epex chat[/]", border_style="green"))

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
