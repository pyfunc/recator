"""
Code refactoring module for eliminating duplicates (simplified)
"""

from typing import List, Dict


class CodeRefactor:
    """Refactor code to eliminate duplicates (planning and preview only)."""

    def __init__(self, config: Dict):
        self.config = config
        self.safe_mode = config.get("safe_mode", True)

    def create_refactoring_plan(self, duplicates: List[Dict]) -> List[Dict]:
        """Create a simplified refactoring plan from detected duplicates."""
        plan: List[Dict] = []
        for dup in duplicates:
            dup_type = dup.get("type", "unknown")
            if dup_type in {"exact", "exact_block", "token_sequence", "similar_block", "structural"}:
                plan.append(
                    {
                        "strategy": self._strategy_for(dup_type),
                        "duplicate": dup,
                        "priority": self._priority_for(dup_type),
                        "description": self._description_for(dup_type),
                    }
                )
        # order by priority
        plan.sort(key=lambda a: a.get("priority", 999))
        return plan

    def preview_refactoring(self, plan: List[Dict]) -> Dict:
        """Return a preview of the refactoring (no file modifications)."""
        affected_files = set()
        est_loc_reduction = 0
        for action in plan:
            dup = action.get("duplicate", {})
            # Estimate LOC reduction: lines * (occurrences-1)
            if "lines" in dup:
                count = dup.get("count", 2)
                est_loc_reduction += int(dup.get("lines", 0)) * max(count - 1, 1)
            # Collect affected files
            if "files" in dup:
                affected_files.update(dup["files"])
            for b in dup.get("blocks", []) or []:
                if isinstance(b, dict) and "file" in b:
                    affected_files.add(b["file"])
        return {
            "total_actions": len(plan),
            "actions": [
                {
                    "strategy": a["strategy"],
                    "description": a["description"],
                    "affected_files": sorted(list(self._affected_files(a))),
                    "confidence": a.get("duplicate", {}).get("confidence", 0.5),
                }
                for a in plan
            ],
            "estimated_loc_reduction": est_loc_reduction,
            "affected_files": sorted(list(affected_files)),
        }

    def apply_refactoring(self, plan: List[Dict]) -> Dict:
        """Dummy implementation: returns success without modifying files.
        Real modifications would require language-specific code transforms.
        """
        return {
            "successful": plan,
            "failed": [],
            "modified_files": [],
            "created_files": [],
        }

    def _affected_files(self, action: Dict) -> set:
        files = set()
        dup = action.get("duplicate", {})
        for f in dup.get("files", []) or []:
            if isinstance(f, str):
                files.add(f)
            elif isinstance(f, dict) and "file" in f:
                files.add(f["file"])
        for b in dup.get("blocks", []) or []:
            if isinstance(b, dict) and "file" in b:
                files.add(b["file"])
        return files

    def _strategy_for(self, dup_type: str) -> str:
        return {
            "exact": "extract_module",
            "exact_block": "extract_method",
            "token_sequence": "parameterize",
            "similar_block": "parameterize",
            "structural": "extract_class",
        }.get(dup_type, "parameterize")

    def _priority_for(self, dup_type: str) -> int:
        return {
            "exact": 1,
            "exact_block": 2,
            "structural": 2,
            "token_sequence": 3,
            "similar_block": 3,
        }.get(dup_type, 5)

    def _description_for(self, dup_type: str) -> str:
        return {
            "exact": "Extract duplicate code to a shared module",
            "exact_block": "Extract duplicate block into a method",
            "token_sequence": "Parameterize similar token sequences",
            "similar_block": "Parameterize similar code blocks",
            "structural": "Extract common structure into a base class",
        }.get(dup_type, "Refactor duplicated logic")
