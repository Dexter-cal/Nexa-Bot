import sys
import asyncio
import argparse
from nexa.interfaces.tui import TUISetupWizard
from nexa.core.engine import engine

async def async_main():
    parser = argparse.ArgumentParser(description="Nexa Bot CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt for Nexa Bot")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--mode", help="Set operational mode")
    parser.add_argument("--role", help="Set agent role")
    parser.add_argument("--spawn", help="Spawn a specialized agent with role")
    parser.add_argument("--chat", action="store_true", help="Start interactive neural chat")
    parser.add_argument("--visuals", action="store_true", help="Display visual mockups of Nexa interfaces")
    parser.add_argument("--quick-setup", action="store_true", help="Fast-track setup with automatic defaults")

    args = parser.parse_args()

    if args.setup:
        wizard = TUISetupWizard()
        await wizard.run()
    elif args.quick_setup:
        await run_quick_setup()
    elif args.visuals:
        from nexa.tools.visualizer import GenerateMockupsTool
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
    from nexa.foundation.storage import SecureConfigStorage
    from nexa.interfaces.prompt_assistant import PromptAssistant

    assistant = PromptAssistant()
    storage = SecureConfigStorage()
    config = await storage.load_config()
    user_name = config.get('user_name', 'User')
    nexa_name = config.get('nexa_name', 'Nexa')

    console = Console()

    banner = Text(r"""
 ⚡ NEXA BOT - NEURAL ORCHESTRATION ENGINE ⚡
    """, style="bold cyan")

    console.print(banner)
    console.print(Panel(f"[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]{nexa_name.upper()} BOT is ready for task orchestration. Type 'exit' or 'quit' to end session.[/]", border_style="sky_blue1"))

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
                nexa_name = config.get('nexa_name', 'Nexa')

                console.print(f"\n[bold sky_blue1]{nexa_name} >[/]")
                console.print(Markdown(result['response']))
                if result.get('switched'):
                    console.print(f"\n[dim italic text_slate_500]Note: Switched from {result['from_model']} to {result['model']} because: {result['switch_reason']}[/]")
            else:
                console.print(f"\n[bold red]Error:[/] {result.get('error', 'Unknown failure')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"\n[bold red]System Error:[/] {e}")

async def run_quick_setup():
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from nexa.intelligence.api_manager import UniversalAPIKeyManager
    from nexa.foundation.storage import SecureConfigStorage
    from nexa.intelligence.defaults import SmartDefaultsEngine

    console = Console()
    console.clear()
    console.print(Panel("[bold green]⚡ NEXA EXPRESS SETUP[/]\n[white]Let's get you online in 30 seconds.[/]", border_style="green"))

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
        "nexa_name": bot_name,
        "api_keys": {}
    })

    if openai_key: config['api_keys']['openai'] = openai_key
    if google_key: config['api_keys']['google'] = google_key

    await storage.store_config(config)

    console.print(Panel.fit(f"[bold green]✓ Express Setup Complete![/]\n[white]Welcome, {user_name}. I am {bot_name}.[/]\nRun: [bold]nexa chat[/]", border_style="green"))

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
