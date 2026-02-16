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

    args = parser.parse_args()

    if args.setup or (not args.prompt and len(sys.argv) == 1 and not args.spawn):
        wizard = TUISetupWizard()
        await wizard.run()
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

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
