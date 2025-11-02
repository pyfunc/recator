#!/usr/bin/env python3
"""
Recator CLI - Command line interface for code duplicate detection and refactoring
"""

import argparse
import json
import sys
from pathlib import Path
from recator import Recator


def print_banner():
    """Print CLI banner"""
    print(
        """
╔═══════════════════════════════════════════╗
║        RECATOR - Code Refactoring Bot     ║
║     Eliminate Code Duplicates with Ease   ║
╚═══════════════════════════════════════════╝
    """
    )


def print_results(results, verbose=False):
    """Print analysis results"""
    print(f"\n📊 Analysis Results:")
    print(f"  • Total files scanned: {results['total_files']}")
    print(f"  • Files parsed: {results['parsed_files']}")
    print(f"  • Duplicates found: {results['duplicates_found']}")

    if results['duplicates_found'] > 0 and verbose:
        print(f"\n📋 Duplicate Details:")
        for i, dup in enumerate(results['duplicates'][:10], 1):
            print(f"\n  [{i}] Type: {dup.get('type', 'unknown')}")

            if 'files' in dup:
                print(f"      Files: {', '.join(dup['files'][:3])}")
                if len(dup['files']) > 3:
                    print(f"             ... and {len(dup['files']) - 3} more")

            if 'confidence' in dup:
                print(f"      Confidence: {dup['confidence']:.2%}")

            if 'lines' in dup:
                print(f"      Lines: {dup['lines']}")


def print_refactoring_preview(preview):
    """Print refactoring preview"""
    print(f"\n🔧 Refactoring Preview:")
    print(f"  • Total actions: {preview['total_actions']}")
    print(f"  • Estimated LOC reduction: {preview['estimated_loc_reduction']}")
    print(f"  • Affected files: {len(preview['affected_files'])}")

    if preview['actions']:
        print(f"\n📝 Planned Actions:")
        for i, action in enumerate(preview['actions'][:5], 1):
            print(f"  [{i}] {action['strategy']}: {action['description']}")
            print(f"      Files: {', '.join(action['affected_files'][:2])}")
            if len(action['affected_files']) > 2:
                print(f"             ... and {len(action['affected_files']) - 2} more")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Recator - Automated code duplicate detection and refactoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument('path', type=str, help='Path to the project directory to analyze')

    parser.add_argument('-a', '--analyze', action='store_true', help='Analyze project for duplicates (default action)')

    parser.add_argument('-r', '--refactor', action='store_true', help='Refactor detected duplicates')

    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview refactoring without applying changes (default: True)')

    # Allow disabling dry-run explicitly without BooleanOptionalAction
    parser.add_argument('--no-dry-run', dest='dry_run', action='store_false', help='Disable dry-run (apply changes where applicable)')

    parser.add_argument('--apply', action='store_true', help='Actually apply refactoring changes (use with caution!)')

    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    parser.add_argument('--min-lines', type=int, default=4, help='Minimum lines for duplicate detection (default: 4)')

    parser.add_argument('--min-tokens', type=int, default=30, help='Minimum tokens for duplicate detection (default: 30)')

    parser.add_argument('--threshold', type=float, default=0.85, help='Similarity threshold (0-1) for fuzzy matching (default: 0.85)')

    parser.add_argument('--languages', nargs='+', default=['python', 'javascript', 'java'], help='Programming languages to analyze (default: python javascript java)')

    parser.add_argument('--exclude', nargs='+', default=['*.min.js', 'node_modules/*', '.git/*'], help='Patterns to exclude from analysis')

    parser.add_argument('--output', type=str, help='Output results to JSON file')

    parser.add_argument('--config', type=str, help='Path to configuration file (JSON)')

    args = parser.parse_args()

    # If --apply is set, disable dry-run implicitly
    if args.apply:
        args.dry_run = False

    if args.verbose:
        print_banner()

    project_path = Path(args.path)
    if not project_path.exists():
        print(f"❌ Error: Path '{args.path}' does not exist")
        sys.exit(1)

    if not project_path.is_dir():
        print(f"❌ Error: Path '{args.path}' is not a directory")
        sys.exit(1)

    config = {
        'min_lines': args.min_lines,
        'min_tokens': args.min_tokens,
        'similarity_threshold': args.threshold,
        'languages': args.languages,
        'exclude_patterns': args.exclude,
        'safe_mode': not args.apply,
    }

    if args.config:
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file: {e}")

    print(f"\n🔍 Initializing Recator for: {project_path.absolute()}")
    recator = Recator(str(project_path), config)

    if args.analyze or not args.refactor:
        print("🔎 Analyzing project for duplicates...")
        results = recator.analyze()
        print_results(results, args.verbose)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {args.output}")
        if results['duplicates_found'] > 0 and not args.refactor:
            print("\n💡 Tip: Use --refactor to see refactoring suggestions")

    if args.refactor:
        print("\n🔧 Planning refactoring...")
        analysis = recator.analyze()
        if analysis['duplicates_found'] == 0:
            print("✅ No duplicates found - nothing to refactor!")
            sys.exit(0)

        if args.apply and not args.dry_run:
            print("\n⚠️  WARNING: About to modify files!")
            confirm = input("Are you sure you want to proceed? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Refactoring cancelled")
                sys.exit(0)
            results = recator.refactor_duplicates(dry_run=False)
            print(f"\n✨ Refactoring complete!")
            print(f"  • Successful: {len(results.get('successful', []))}")
            print(f"  • Failed: {len(results.get('failed', []))}")
            print(f"  • Modified files: {len(results.get('modified_files', []))}")
            if results.get('failed'):
                print("\n❌ Failed refactorings:")
                for fail in results['failed'][:5]:
                    print(f"  • {fail['error']}")
        else:
            results = recator.refactor_duplicates(dry_run=True)
            print_refactoring_preview(results)
            if not args.dry_run:
                print("\n💡 Tip: Use --apply to actually apply these changes")
            else:
                print("\n💡 Tip: Use --apply --no-dry-run to apply these changes")

    print("\n✅ Done!")


if __name__ == '__main__':
    main()
