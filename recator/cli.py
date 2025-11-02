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


def print_results(results, verbose=False, show_snippets=False, max_show=10, snippet_lines=10, max_blocks=0, suppress_duplicates=True):
    """Print analysis results (optionally with code snippets)."""
    print(f"\n📊 Analysis Results:")
    print(f"  • Total files scanned: {results['total_files']}")
    print(f"  • Files parsed: {results['parsed_files']}")
    print(f"  • Duplicates found: {results['duplicates_found']}")
    
    if results['duplicates_found'] > 0 and (verbose or show_snippets):
        print(f"\n📋 Duplicate Details:")
        dup_list = results['duplicates']
        if isinstance(max_show, int) and max_show > 0:
            dup_list = results['duplicates'][:max_show]
        if suppress_duplicates:
            dup_list = _suppress_redundant_duplicates(dup_list)
        for i, dup in enumerate(dup_list, 1):
            print(f"\n  [{i}] Type: {dup.get('type', 'unknown')}")
            
            if 'files' in dup:
                files = [str(Path(p).resolve()) for p in dup['files']]
                print("      Files:")
                for j, fp in enumerate(files, 1):
                    print(f"        - [{j}] {fp}")
            
            if 'confidence' in dup:
                print(f"      Confidence: {dup['confidence']:.2%}")
            
            if 'lines' in dup:
                print(f"      Lines: {dup['lines']}")

            # Representative snippet ONCE per duplicate (blocks)
            if 'blocks' in dup and dup['blocks']:
                first_b = dup['blocks'][0] if isinstance(dup['blocks'][0], dict) else None
                if first_b:
                    fpath0 = str(Path(first_b.get('file', '')).resolve())
                    code0 = (first_b.get('content', '') or '').strip()
                    if code0:
                        lang0 = 'css' if dup.get('type') == 'css_block' else lang_for_path(fpath0)
                        if show_snippets:
                            print("      Snippet:")
                            print("\n" + f"```{lang0}\n" + code0 + "\n```" + "\n")
                        elif verbose:
                            lines = code0.splitlines()
                            head = "\n".join(lines[:snippet_lines])
                            if len(lines) > snippet_lines:
                                head += "\n..."
                            print("      Snippet:")
                            print("\n" + f"```{lang0}\n" + head + "\n```" + "\n")

            # Show full absolute paths with ranges for block/token duplicates
            if 'blocks' in dup and dup['blocks']:
                print("      Blocks:")
                blocks_list = dup['blocks']
                if isinstance(max_blocks, int) and max_blocks > 0:
                    blocks_list = dup['blocks'][:max_blocks]
                for j, b in enumerate(blocks_list, 1):
                    if isinstance(b, dict):
                        fpath = str(Path(b.get('file', '')).resolve())
                        start = b.get('start_line', '?')
                        end = b.get('end_line', '?')
                        print(f"        - [{j}] {fpath}:{start}-{end}")
                shown = len(blocks_list)
                more = max(0, len(dup['blocks']) - shown)
                if more:
                    print(f"             ... and {more} more blocks")

            if 'groups' in dup and dup['groups']:
                # Representative tokens preview ONCE per duplicate
                first_g = dup['groups'][0] if isinstance(dup['groups'][0], dict) else None
                if first_g and show_snippets:
                    toks = first_g.get('tokens', []) or []
                    preview = ' '.join(toks[:50]) + (" ..." if len(toks) > 50 else "")
                    print("      Tokens:")
                    print("\n" + f"```\n" + preview + "\n```" + "\n")
                print("      Token groups:")
                groups_list = dup['groups']
                if isinstance(max_blocks, int) and max_blocks > 0:
                    groups_list = dup['groups'][:max_blocks]
                for j, g in enumerate(groups_list, 1):
                    if isinstance(g, dict):
                        fpath = str(Path(g.get('file', '')).resolve())
                        pos = g.get('position', '?')
                        print(f"        - [{j}] {fpath} @ token_pos={pos}")
                shown = len(groups_list)
                more = max(0, len(dup['groups']) - shown)
                if more:
                    print(f"             ... and {more} more groups")

            # Fallback snippet for other types
            if show_snippets and not (dup.get('blocks') or dup.get('groups')):
                snippet = get_duplicate_snippet(dup)
                if snippet:
                    lang = guess_fence_language(dup)
                    print("      Code snippet:")
                    print("\n" + f"```{lang}\n" + snippet.strip() + "\n```" + "\n")

def print_refactoring_preview(preview):
    """Print refactoring preview"""
    print(f"\n🔧 Refactoring Preview:")
    print(f"  • Total actions: {preview['total_actions']}")
    print(f"  • Estimated LOC reduction: {preview['estimated_loc_reduction']}")
    print(f"  • Affected files: {len(preview['affected_files'])}")
    if preview['actions']:
        print(f"\n📝 Planned Actions:")
        for i, action in enumerate(preview['actions'][:10], 1):
            print(f"  [{i}] {action['strategy']}: {action['description']}")
            if action.get('affected_files'):
                print(f"      Files: {', '.join(action['affected_files'][:3])}")
                more = max(0, len(action['affected_files']) - 3)
                if more:
                    print(f"             ... and {more} more")


# ---------- Helpers ----------

def parse_selection(spec: str):
    """Parse selection string like '1,3-5' into a set of ints."""
    result = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            try:
                start = int(a)
                end = int(b)
                if start <= end:
                    result.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                result.add(int(part))
            except ValueError:
                continue
    return sorted(result)


def guess_fence_language(dup: dict) -> str:
    """Guess code fence language from duplicate metadata."""
    # Prefer file extension from first block/file
    path = None
    if 'blocks' in dup and dup['blocks']:
        b = dup['blocks'][0]
        path = b.get('file') if isinstance(b, dict) else None
    elif 'files' in dup and dup['files']:
        path = dup['files'][0]
    if path:
        p = str(path).lower()
        if p.endswith(('.ts', '.tsx')):
            return 'ts'
        if p.endswith(('.js', '.jsx')):
            return 'js'
        if p.endswith(('.css', '.scss', '.sass', '.less', '.styl')):
            return 'css'
        if p.endswith(('.html', '.htm')):
            return 'html'
        if p.endswith('.py'):
            return 'python'
        if p.endswith(('.java',)):
            return 'java'
        if p.endswith(('.c', '.h')):
            return 'c'
        if p.endswith(('.cpp', '.cc', '.cxx', '.hpp')):
            return 'cpp'
    return ''


def _suppress_redundant_duplicates(dups: list) -> list:
    """Suppress redundant duplicate groups to avoid repeated info.

    Rules:
    - If a duplicate has a 'hash' seen earlier, drop it.
    - For 'exact': dedup by sorted tuple of files.
    - For 'exact_block': keep first group; drop later groups whose every block
      range is covered by previously kept block ranges in the same file(s).
    - For others: only dedup by simple string key.
    """
    seen_hashes = set()
    seen_exact_files = set()
    coverage = {}  # file -> list[(start,end)] kept so far
    result = []

    def is_covered(file_path: str, start: int, end: int) -> bool:
        intervals = coverage.get(file_path, [])
        length = max(1, end - start + 1)
        for a, b in intervals:
            overlap = max(0, min(b, end) - max(a, start) + 1)
            # Consider covered if there is substantial overlap (>=60%)
            if overlap >= max(1, int(0.6 * length)):
                return True
        return False

    def add_interval(file_path: str, start: int, end: int):
        coverage.setdefault(file_path, []).append((start, end))

    for dup in dups:
        dtype = dup.get('type')
        if 'hash' in dup:
            h = dup['hash']
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

        if dtype in ('exact', 'fuzzy'):
            key = tuple(sorted(dup.get('files', [])))
            if key in seen_exact_files:
                continue
            seen_exact_files.add(key)
            result.append(dup)
            continue

        if dtype == 'exact_block' and dup.get('blocks'):
            blocks = [b for b in dup['blocks'] if isinstance(b, dict)]
            if blocks:
                # If all blocks covered by previous intervals, skip
                all_cov = True
                for b in blocks:
                    f = str(b.get('file', ''))
                    s = int(b.get('start_line', 0) or 0)
                    e = int(b.get('end_line', s) or s)
                    if not is_covered(f, s, e):
                        all_cov = False
                        break
                if all_cov:
                    continue
                # Keep and register intervals
                for b in blocks:
                    f = str(b.get('file', ''))
                    s = int(b.get('start_line', 0) or 0)
                    e = int(b.get('end_line', s) or s)
                    add_interval(f, s, e)
            result.append(dup)
            continue

        # default: keep (after hash-based dedup)
        result.append(dup)

    return result


def lang_for_path(path: str) -> str:
    """Guess code fence language from a file path."""
    p = str(path).lower()
    if p.endswith(('.ts', '.tsx')):
        return 'ts'
    if p.endswith(('.js', '.jsx')):
        return 'js'
    if p.endswith(('.css', '.scss', '.sass', '.less', '.styl')):
        return 'css'
    if p.endswith(('.html', '.htm')):
        return 'html'
    if p.endswith('.py'):
        return 'python'
    if p.endswith(('.java',)):
        return 'java'
    if p.endswith(('.c', '.h')):
        return 'c'
    if p.endswith(('.cpp', '.cc', '.cxx', '.hpp')):
        return 'cpp'
    if p.endswith(('.rb',)):
        return 'ruby'
    if p.endswith(('.php',)):
        return 'php'
    if p.endswith(('.go',)):
        return 'go'
    if p.endswith(('.rs',)):
        return 'rust'
    if p.endswith(('.kt', '.kts')):
        return 'kotlin'
    if p.endswith(('.swift',)):
        return 'swift'
    return ''


def get_duplicate_snippet(dup: dict) -> str:
    """Return a code snippet for a duplicate, when available."""
    t = dup.get('type')
    # exact_block: blocks contain 'content'
    if t == 'exact_block' and 'blocks' in dup and dup['blocks']:
        blk = dup['blocks'][0]
        return blk.get('content', '') or ''
    # token_sequence: show joined tokens preview
    if t == 'token_sequence' and 'groups' in dup and dup['groups']:
        toks = dup['groups'][0].get('tokens', [])
        preview = ' '.join(toks[:50])
        if len(toks) > 50:
            preview += ' ...'
        return preview
    # exact (whole-file): show small head to avoid spam
    if t == 'exact' and 'files' in dup and dup['files']:
        try:
            with open(dup['files'][0], 'r', encoding='utf-8', errors='ignore') as f:
                return ''.join(f.readlines()[:20])
        except Exception:
            return ''
    return ''


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
    parser.add_argument('--no-dry-run', dest='dry_run', action='store_false', help='Disable dry-run (apply changes where applicable)')
    parser.add_argument('--apply', action='store_true', help='Actually apply refactoring changes (use with caution!)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Show duplicate code snippets and control output size
    parser.add_argument('--show-snippets', action='store_true', help='Show code snippets for duplicates (where available)')
    parser.add_argument('--max-show', type=int, default=10, help='Max number of duplicates to display (0 = unlimited, default: 10)')
    parser.add_argument('--snippet-lines', type=int, default=10, help='Lines to show per block snippet in verbose mode (default: 10)')
    parser.add_argument('--max-blocks', type=int, default=0, help='Max blocks/groups per duplicate to display (0 = unlimited, default: 0)')
    parser.add_argument('--no-suppress-duplicates', action='store_true', help='Do not suppress overlapping duplicate groups in output')

    # Refactor on demand: select which duplicates to refactor
    parser.add_argument('--select', type=str, help='Comma-separated duplicate IDs or ranges to refactor, e.g. 1,3-5')
    parser.add_argument('--interactive', action='store_true', help='Interactive selection of duplicates to refactor')

    parser.add_argument('--min-lines', type=int, default=4, help='Minimum lines for duplicate detection (default: 4)')
    parser.add_argument('--min-tokens', type=int, default=30, help='Minimum tokens for duplicate detection (default: 30)')
    parser.add_argument('--threshold', type=float, default=0.85, help='Similarity threshold (0-1) for fuzzy matching (default: 0.85)')
    parser.add_argument('--languages', nargs='+', default=['python', 'javascript', 'java', 'html', 'css'], help='Programming languages to analyze (default: python javascript java html css)')
    parser.add_argument('--exclude', nargs='+', default=['*.min.js', 'node_modules/*', '.git/*'], help='Patterns to exclude from analysis')
    parser.add_argument('--output', type=str, help='Output results to JSON file')
    parser.add_argument('--config', type=str, help='Path to configuration file (JSON)')

    args = parser.parse_args()

    # If --apply is set, disable dry-run implicitly
    if args.apply:
        args.dry_run = False

    # Print banner
    if args.verbose:
        print_banner()

    # Validate path
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"❌ Error: Path '{args.path}' does not exist")
        sys.exit(1)
    if not project_path.is_dir():
        print(f"❌ Error: Path '{args.path}' is not a directory")
        sys.exit(1)

    # Load configuration
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

    # Analyze
    if args.analyze or not args.refactor:
        print("🔎 Analyzing project for duplicates...")
        results = recator.analyze()
        print_results(results, verbose=args.verbose, show_snippets=args.show_snippets, max_show=args.max_show, snippet_lines=args.snippet_lines, max_blocks=args.max_blocks, suppress_duplicates=not args.no_suppress_duplicates)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {args.output}")
        if results['duplicates_found'] > 0 and not args.refactor:
            print("\n💡 Tip: Use --refactor to see refactoring suggestions")

    # Refactor
    if args.refactor:
        print("\n🔧 Planning refactoring...")
        analysis = recator.analyze()
        if analysis['duplicates_found'] == 0:
            print("✅ No duplicates found - nothing to refactor!")
            sys.exit(0)

        # Selection
        selection_ids = []
        if args.select:
            selection_ids = parse_selection(args.select)
        elif args.interactive:
            print_results(analysis, verbose=True, show_snippets=True, max_show=min(args.max_show, 10) if args.max_show > 0 else 0, snippet_lines=args.snippet_lines, max_blocks=args.max_blocks, suppress_duplicates=not args.no_suppress_duplicates)
            raw = input("Enter duplicate IDs to refactor (e.g., 1,3-5) or leave empty to cancel: ").strip()
            if not raw:
                print("❌ Refactoring cancelled")
                sys.exit(0)
            selection_ids = parse_selection(raw)

        selected_dups = analysis['duplicates']
        if selection_ids:
            selected_dups = [d for idx, d in enumerate(analysis['duplicates'], start=1) if idx in selection_ids]
            if not selected_dups:
                print("❌ No valid duplicate IDs selected")
                sys.exit(1)

        if args.apply and not args.dry_run:
            print("\n⚠️  WARNING: About to modify files!")
            confirm = input("Are you sure you want to proceed? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Refactoring cancelled")
                sys.exit(0)
            results = recator.refactor_duplicates(duplicates=selected_dups, dry_run=False)
            print(f"\n✨ Refactoring complete!")
            print(f"  • Successful: {len(results.get('successful', []))}")
            print(f"  • Failed: {len(results.get('failed', []))}")
            print(f"  • Modified files: {len(results.get('modified_files', []))}")
            if results.get('failed'):
                print("\n❌ Failed refactorings:")
                for fail in results['failed'][:5]:
                    print(f"  • {fail['error']}")
        else:
            results = recator.refactor_duplicates(duplicates=selected_dups, dry_run=True)
            print_refactoring_preview(results)
            if not args.dry_run:
                print("\n💡 Tip: Use --apply to actually apply these changes")
            else:
                print("\n💡 Tip: Use --apply --no-dry-run to apply these changes")

    print("\n✅ Done!")

if __name__ == '__main__':
    main()
