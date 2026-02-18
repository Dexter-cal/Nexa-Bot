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

    args = parser.parse_args()

    if args.setup:
        wizard = TUISetupWizard()
        await wizard.run()
    elif args.chat or (not args.prompt and len(sys.argv) == 1 and not args.spawn):
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
    from nexa.foundation.storage import SecureConfigStorage

    storage = SecureConfigStorage()
    config = await storage.load_config()
    user_name = config.get('user_name', 'User')
    nexa_name = config.get('nexa_name', 'Nexa')

    console = Console()
    console.print(Panel(f"[bold sky_blue1]Neural Chat Interface Initialized[/]\n[italic text_slate_500]{nexa_name.upper()} BOT is ready for task orchestration. Type 'exit' or 'quit' to end session.[/]", border_style="sky_blue1"))

    while True:
        try:
            user_input = console.input(f"\n[bold sky_blue1]{user_name} > [/]")
            if user_input.lower() in ["exit", "quit"]:
                break

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

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
