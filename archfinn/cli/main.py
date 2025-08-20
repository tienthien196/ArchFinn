# archfinn/cli/main.py
import argparse
import sys
import traceback
from pathlib import Path
from archfinn.parser.parser import parse_file
from archfinn.core.engine import ArchState, run_scenario


def print_banner():
    print(r"""
    █████╗  ██████╗  ██████╗██╗  ██╗███████╗██╗███╗   ██╗███╗   ██╗
    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██║████╗  ██║████╗  ██║
    ███████║██████╔╝██║     ███████║█████╗  ██║██╔██╗ ██║██╔██╗ ██║
    ██╔══██║██╔══██╗██║     ██╔══██║██╔══╝  ██║██║╚██╗██║██║╚██╗██║
    ██║  ██║██║  ██║╚██████╗██║  ██║██║     ██║██║ ╚████║██║ ╚████║
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝
    
    🚀 Where Ideas Become Architectures
    """)


def validate_file(file_path: str) -> Path:
    """Validate input file exists and has correct extension"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if not path.suffix.lower() == '.afinn':
        print(f"⚠️  Warning: Expected .afinn extension, got {path.suffix}")
    
    return path


def main():
    parser = argparse.ArgumentParser(
        description="ArchFinn Script Engine - Architecture Simulation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  archfinn scenario.afinn              # Run first scenario in file
  archfinn scenario.afinn --debug      # Run with debug output
  archfinn scenario.afinn --seed 42    # Run with custom random seed
        """
    )
    
    parser.add_argument("file", help="Path to .afinn scenario file")
    parser.add_argument("--scenario", "-s", help="Specific scenario name to run")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed for simulation")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress banner and extra output")
    
    args = parser.parse_args()

    # Validate input file
    file_path = validate_file(args.file)
    
    if not args.quiet:
        print_banner()
        print(f"📁 Loading scenario: {file_path.name}")

    # Parse the scenario file
    try:
        ast = parse_file(str(file_path))
        if args.debug:
            print(f"🔍 Debug: Parsed AST type: {type(ast)}")
            
    except Exception as e:
        print(f"❌ Parse error: {e}")
        if args.debug:
            print("\n🔍 Debug traceback:")
            traceback.print_exc()
        sys.exit(1)

    if ast is None:
        print("❌ Parse failed: AST is None")
        sys.exit(1)

    # Find target scenario
    scenarios = ast if isinstance(ast, list) else [ast]
    scenario = None
    
    if args.scenario:
        # Look for specific scenario by name
        for item in scenarios:
            if hasattr(item, "name") and item.name == args.scenario:
                scenario = item
                break
        if not scenario:
            available = [item.name for item in scenarios if hasattr(item, "name")]
            print(f"❌ Scenario '{args.scenario}' not found.")
            print(f"Available scenarios: {', '.join(available)}")
            sys.exit(1)
    else:
        # Use first valid scenario
        for item in scenarios:
            if hasattr(item, "name"):
                scenario = item
                break

    if scenario is None:
        print("❌ No valid scenario found in file.")
        print("Make sure your file contains a SCENARIO or SIMULATION block.")
        sys.exit(1)

    if not args.quiet:
        print(f"🎯 Running scenario: {scenario.name}")
        print(f"🎲 Random seed: {args.seed}")
        print("─" * 60)

    # Initialize and run simulation
    try:
        state = ArchState(nodes={}, edges=[], controls={})
        state.rng.seed(args.seed)
        
        result = run_scenario(state, scenario)
        
        # Print results
        if not args.quiet:
            print("─" * 60)
            print(f"📊 Simulation completed in {state.tick} steps")
            print(f"🎯 Final result: {result['result'].upper()}")
            
            if result.get('events'):
                print(f"⚠️  Events triggered: {', '.join(result['events'])}")
        else:
            # Quiet mode: just print essential info
            print(f"RESULT: {result['result']}")
            if result.get('events'):
                print(f"EVENTS: {','.join(result['events'])}")

    except Exception as e:
        print(f"❌ Runtime error: {e}")
        if args.debug:
            print("\n🔍 Debug traceback:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()