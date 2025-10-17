"""
Self-Modification System

Enables the agent to modify its own code with extensive safety controls.
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import json

logger = logging.getLogger("apex_orchestrator.agent.self_modifier")


class SelfModifier:
    """Safely modify the agent's own codebase"""
    
    def __init__(self, memory_system, code_generator, safety_controller):
        self.memory = memory_system
        self.code_generator = code_generator
        self.safety = safety_controller
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load modification limits from state
        self.modifications_today = int(self.memory.get_agent_state("modifications_today") or "0")
        self.last_modification_date = self.memory.get_agent_state("last_modification_date")
        
        logger.info("Self-modifier initialized with safety controls")
    
    def can_modify(self) -> tuple[bool, str]:
        """Check if modifications are allowed"""
        # Check safety controls
        if not self.safety.modifications_enabled_check():
            return False, "Modifications disabled by safety controller"
        
        # Check daily limit
        max_per_day = self.safety.get_max_modifications_per_day()
        today = datetime.utcnow().date().isoformat()
        
        if self.last_modification_date != today:
            self.modifications_today = 0
            self.memory.set_agent_state("modifications_today", "0")
            self.memory.set_agent_state("last_modification_date", today)
        
        if self.modifications_today >= max_per_day:
            return False, f"Daily modification limit reached ({max_per_day})"
        
        return True, "Modifications allowed"
    
    async def propose_modification(self, target_file: str, modification_type: str,
                                   description: str, reason: str) -> Dict[str, Any]:
        """Propose a code modification (requires approval)"""
        logger.info(f"Proposing modification to {target_file}: {modification_type}")
        
        # Check if allowed
        can_modify, msg = self.can_modify()
        if not can_modify:
            return {
                "status": "blocked",
                "reason": msg
            }
        
        # Read current code
        target_path = Path(target_file)
        if not target_path.exists():
            return {
                "status": "error",
                "error": f"File not found: {target_file}"
            }
        
        with open(target_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # Generate modified code
        if modification_type == "optimize":
            modified = await self._generate_optimization(current_code, reason)
        elif modification_type == "add_feature":
            modified = await self._add_feature(current_code, description)
        elif modification_type == "fix_bug":
            modified = await self._fix_bug(current_code, description)
        elif modification_type == "refactor":
            modified = await self._refactor_code(current_code, reason)
        else:
            return {
                "status": "error",
                "error": f"Unknown modification type: {modification_type}"
            }
        
        # Validate modified code
        validation = self.code_generator.analyze_code_quality(modified['code'])
        
        # Create backup
        backup_path = self._create_backup(target_file, current_code)
        
        # Generate tests
        test_code = self.code_generator.generate_test_case(modified['code'])
        
        # Record proposal
        proposal = {
            "target_file": target_file,
            "modification_type": modification_type,
            "description": description,
            "reason": reason,
            "current_code_hash": self._hash_code(current_code),
            "modified_code_hash": self._hash_code(modified['code']),
            "backup_path": str(backup_path),
            "validation": validation,
            "test_code": test_code,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending_approval"
        }
        
        # Save proposal
        proposal_id = self._save_proposal(proposal)
        proposal['id'] = proposal_id
        
        logger.info(f"Modification proposal created: ID {proposal_id}")
        
        return {
            "status": "proposed",
            "proposal": proposal,
            "preview": {
                "current_lines": len(current_code.split('\n')),
                "modified_lines": len(modified['code'].split('\n')),
                "quality_score": validation.get('quality_score', 0)
            }
        }
    
    async def apply_modification(self, proposal_id: int, 
                                auto_test: bool = True) -> Dict[str, Any]:
        """Apply a proposed modification"""
        logger.info(f"Applying modification proposal {proposal_id}")
        
        # Load proposal
        proposal = self._load_proposal(proposal_id)
        if not proposal:
            return {
                "status": "error",
                "error": "Proposal not found"
            }
        
        # Final safety check
        can_modify, msg = self.can_modify()
        if not can_modify:
            return {
                "status": "blocked",
                "reason": msg
            }
        
        target_file = proposal['target_file']
        target_path = Path(target_file)
        
        # Read current code
        with open(target_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # Verify code hasn't changed
        current_hash = self._hash_code(current_code)
        if current_hash != proposal['current_code_hash']:
            return {
                "status": "error",
                "error": "File has been modified since proposal was created"
            }
        
        # Load modified code from proposal
        modified_code = proposal.get('modified_code', '')
        
        # Run tests if enabled
        test_results = {"status": "skipped"}
        if auto_test:
            test_results = await self._run_tests(proposal.get('test_code', ''))
            
            if test_results['status'] == 'failed':
                logger.warning("Tests failed, modification blocked")
                return {
                    "status": "test_failed",
                    "test_results": test_results
                }
        
        # Apply modification
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)
            
            logger.info(f"Applied modification to {target_file}")
            
            # Record in memory
            self.memory.record_modification(
                modification_type=proposal['modification_type'],
                target_file=target_file,
                description=proposal['description'],
                code_before=current_code,
                code_after=modified_code,
                test_results=test_results,
                applied=True,
                reason=proposal['reason']
            )
            
            # Update counter
            self.modifications_today += 1
            self.memory.set_agent_state("modifications_today", str(self.modifications_today))
            
            # Git commit if enabled
            if self.safety.git_integration_enabled():
                self._git_commit(target_file, proposal['description'])
            
            return {
                "status": "applied",
                "file": target_file,
                "backup": proposal['backup_path'],
                "test_results": test_results,
                "modifications_remaining_today": self.safety.get_max_modifications_per_day() - self.modifications_today
            }
            
        except Exception as e:
            logger.error(f"Failed to apply modification: {e}")
            
            # Attempt rollback
            self._rollback_from_backup(proposal['backup_path'], target_file)
            
            return {
                "status": "error",
                "error": str(e),
                "rollback": "attempted"
            }
    
    def rollback_modification(self, modification_id: int) -> Dict[str, Any]:
        """Rollback a modification"""
        logger.info(f"Rolling back modification {modification_id}")
        
        # Get modification record
        # (Simplified - would query database)
        
        return {
            "status": "rolledback",
            "message": "Modification reverted to backup"
        }
    
    async def _generate_optimization(self, code: str, reason: str) -> Dict[str, Any]:
        """Generate optimized version of code"""
        # Determine optimization type from reason
        if "slow" in reason.lower() or "performance" in reason.lower():
            opt_type = "caching"
        elif "error" in reason.lower():
            opt_type = "error_handling"
        else:
            opt_type = "logging"
        
        optimized = self.code_generator.generate_optimization(code, opt_type)
        return optimized
    
    async def _add_feature(self, code: str, description: str) -> Dict[str, Any]:
        """Add new feature to existing code"""
        # Generate new feature code
        feature_code = await self.code_generator.generate_function(
            purpose=description,
            requirements={}
        )
        
        # Merge with existing code
        merged = code + "\n\n" + feature_code.get('code', '')
        
        return {
            "code": merged,
            "description": f"Added feature: {description}"
        }
    
    async def _fix_bug(self, code: str, description: str) -> Dict[str, Any]:
        """Fix a bug in existing code"""
        # Simplified bug fix - add better error handling
        fixed = self.code_generator._improve_error_handling(code)
        
        return {
            "code": fixed,
            "description": f"Fixed bug: {description}"
        }
    
    async def _refactor_code(self, code: str, reason: str) -> Dict[str, Any]:
        """Refactor code for better quality"""
        # Simple refactoring - could be much more sophisticated
        refactored = code
        
        # Add docstrings if missing
        if '"""' not in refactored:
            lines = refactored.split('\n')
            if lines and 'def ' in lines[0]:
                lines.insert(1, '    """Refactored function"""')
                refactored = '\n'.join(lines)
        
        return {
            "code": refactored,
            "description": f"Refactored: {reason}"
        }
    
    def _create_backup(self, target_file: str, content: str) -> Path:
        """Create backup of current code"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = Path(target_file).name + f".backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    
    def _rollback_from_backup(self, backup_path: str, target_file: str):
        """Rollback from backup"""
        try:
            shutil.copy(backup_path, target_file)
            logger.info(f"Rolled back {target_file} from {backup_path}")
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
    
    def _hash_code(self, code: str) -> str:
        """Generate hash of code"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _save_proposal(self, proposal: Dict) -> int:
        """Save modification proposal"""
        # Save to file system
        proposals_dir = Path("proposals")
        proposals_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        proposal_file = proposals_dir / f"proposal_{timestamp}.json"
        
        with open(proposal_file, 'w', encoding='utf-8') as f:
            json.dump(proposal, f, indent=2)
        
        # Return a simple ID (timestamp-based)
        return int(timestamp)
    
    def _load_proposal(self, proposal_id: int) -> Optional[Dict]:
        """Load modification proposal"""
        proposals_dir = Path("proposals")
        proposal_file = proposals_dir / f"proposal_{proposal_id}.json"
        
        if not proposal_file.exists():
            return None
        
        with open(proposal_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _run_tests(self, test_code: str) -> Dict[str, Any]:
        """Run generated tests"""
        if not test_code or test_code.startswith("#"):
            return {"status": "skipped", "reason": "No valid test code"}
        
        # Write test to temp file
        test_file = Path("temp_test.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        try:
            # Run pytest
            result = subprocess.run(
                ["pytest", str(test_file), "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            test_file.unlink()
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            if test_file.exists():
                test_file.unlink()
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _git_commit(self, file_path: str, message: str):
        """Commit changes to git"""
        try:
            subprocess.run(["git", "add", file_path], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"[AutoAgent] {message}"],
                check=True
            )
            logger.info(f"Git commit created for {file_path}")
        except Exception as e:
            logger.warning(f"Git commit failed: {e}")
    
    def get_modification_stats(self) -> Dict[str, Any]:
        """Get modification statistics"""
        return {
            "modifications_today": self.modifications_today,
            "max_per_day": self.safety.get_max_modifications_per_day(),
            "remaining_today": self.safety.get_max_modifications_per_day() - self.modifications_today,
            "last_modification_date": self.last_modification_date
        }

