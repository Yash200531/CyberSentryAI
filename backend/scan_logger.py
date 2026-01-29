"""
Unified Scan Logger
Stores all scan results, DNA fingerprints, and red-team analysis
Provides export and query capabilities
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib


class ScanLogger:
    """
    Unified logging system for all scans
    Stores: raw input, model outputs, red-team analysis, cyber DNA
    """
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.datasets_dir = Path("datasets")
        self.exports_dir = Path("exports")
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.datasets_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        
        # Log files
        self.scan_log_file = self.logs_dir / "scans.jsonl"
        self.dna_log_file = self.logs_dir / "cyber_dna.jsonl"
        self.redteam_log_file = self.logs_dir / "redteam_analysis.jsonl"
        self.daily_stats_file = self.logs_dir / "daily_stats.json"
        
    def log_scan(
        self,
        scan_type: str,
        raw_input: Any,
        scan_result: Dict[str, Any],
        redteam_result: Optional[Dict[str, Any]],
        cyber_dna: Optional[Dict[str, Any]],
        user_id: Optional[str] = None,
        user_ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log complete scan with all components
        
        Args:
            scan_type: 'text', 'url', 'image', 'email'
            raw_input: Original input (text, URL, image reference)
            scan_result: Primary detection results
            redteam_result: Red-team analysis
            cyber_dna: Cyber DNA fingerprint
            user_id: Optional user identifier
            user_ip: User IP address
            metadata: Additional metadata
            
        Returns:
            Scan ID (hash)
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Generate unique scan ID
        scan_id = self._generate_scan_id(scan_type, raw_input, timestamp)
        
        # Prepare complete log entry
        log_entry = {
            "scan_id": scan_id,
            "scan_type": scan_type,
            "timestamp": timestamp,
            "user_id": user_id,
            "user_ip": user_ip,
            "raw_input": self._sanitize_input(raw_input, scan_type),
            "scan_result": scan_result,
            "redteam_analysis": redteam_result,
            "cyber_dna": self._sanitize_dna_for_log(cyber_dna),
            "metadata": metadata or {},
            "threat_detected": self._is_threat_detected(scan_result),
            "overall_confidence": scan_result.get("score", 0) * 100 if "score" in scan_result else 0
        }
        
        # Write to main scan log
        self._append_jsonl(self.scan_log_file, log_entry)
        
        # Write to specialized logs
        if redteam_result:
            self._log_redteam(scan_id, timestamp, scan_type, redteam_result)
        
        if cyber_dna:
            self._log_dna(scan_id, timestamp, scan_type, cyber_dna)
        
        # Update daily statistics
        self._update_daily_stats(scan_type, log_entry["threat_detected"])
        
        return scan_id
    
    def get_scan_history(
        self, 
        scan_type: Optional[str] = None,
        limit: int = 100,
        threat_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve scan history
        
        Args:
            scan_type: Filter by type ('text', 'url', 'image')
            limit: Maximum number of records
            threat_only: Only return threats
            
        Returns:
            List of scan records
        """
        if not self.scan_log_file.exists():
            return []
        
        results = []
        
        with open(self.scan_log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if scan_type and entry.get("scan_type") != scan_type:
                        continue
                    
                    if threat_only and not entry.get("threat_detected"):
                        continue
                    
                    results.append(entry)
                    
                    if len(results) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        # Return most recent first
        return list(reversed(results))
    
    def get_dna_database(
        self, 
        threat_only: bool = True,
        min_confidence: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Get all DNA fingerprints for similarity matching
        
        Args:
            threat_only: Only return threat DNAs
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of DNA fingerprints
        """
        if not self.dna_log_file.exists():
            return []
        
        results = []
        
        with open(self.dna_log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    dna = entry.get("cyber_dna", {})
                    
                    # Apply filters
                    if threat_only and dna.get("overall_threat_score", 0) < min_confidence:
                        continue
                    
                    results.append(dna)
                    
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """Get today's statistics"""
        if not self.daily_stats_file.exists():
            return self._empty_stats()
        
        try:
            with open(self.daily_stats_file, "r", encoding="utf-8") as f:
                stats = json.load(f)
            
            # Check if it's today's data
            today = datetime.utcnow().date().isoformat()
            if stats.get("date") == today:
                return stats
            else:
                # New day, reset stats
                return self._empty_stats()
                
        except (json.JSONDecodeError, IOError):
            return self._empty_stats()
    
    def export_dataset(
        self,
        scan_type: str,
        output_format: str = "json",
        threat_only: bool = False
    ) -> str:
        """
        Export scan data as dataset
        
        Args:
            scan_type: Type to export
            output_format: 'json' or 'csv'
            threat_only: Only export threats
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{scan_type}_dataset_{timestamp}.{output_format}"
        output_path = self.exports_dir / filename
        
        # Get data
        data = self.get_scan_history(scan_type=scan_type, limit=10000, threat_only=threat_only)
        
        if output_format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif output_format == "csv":
            self._export_csv(output_path, data, scan_type)
        
        return str(output_path)
    
    def _generate_scan_id(self, scan_type: str, raw_input: Any, timestamp: str) -> str:
        """Generate unique scan ID"""
        content = f"{scan_type}|{str(raw_input)[:200]}|{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _sanitize_input(self, raw_input: Any, scan_type: str) -> Any:
        """Sanitize input for logging"""
        if scan_type == "text" and isinstance(raw_input, str):
            # Truncate very long text
            return raw_input[:1000] if len(raw_input) > 1000 else raw_input
        elif scan_type == "url":
            return str(raw_input)
        elif scan_type == "image":
            # For images, log reference/ID instead of raw bytes
            if isinstance(raw_input, dict):
                return raw_input.get("image_id", "unknown")
            return str(raw_input)
        return raw_input
    
    def _sanitize_dna_for_log(self, cyber_dna: Optional[Dict]) -> Optional[Dict]:
        """Remove full embedding vector from log (too large)"""
        if not cyber_dna:
            return None
        
        # Create copy without full embedding
        sanitized = cyber_dna.copy()
        if "embedding_full" in sanitized:
            del sanitized["embedding_full"]
        
        return sanitized
    
    def _is_threat_detected(self, scan_result: Dict[str, Any]) -> bool:
        """Check if scan detected a threat"""
        return bool(
            scan_result.get("is_scam") or
            scan_result.get("is_phishing") or
            scan_result.get("is_fake", False)
        )
    
    def _log_redteam(
        self, 
        scan_id: str, 
        timestamp: str, 
        scan_type: str, 
        redteam_result: Dict
    ):
        """Log red-team analysis separately"""
        entry = {
            "scan_id": scan_id,
            "timestamp": timestamp,
            "scan_type": scan_type,
            "analysis": redteam_result
        }
        self._append_jsonl(self.redteam_log_file, entry)
    
    def _log_dna(
        self, 
        scan_id: str, 
        timestamp: str, 
        scan_type: str, 
        cyber_dna: Dict
    ):
        """Log cyber DNA separately"""
        entry = {
            "scan_id": scan_id,
            "timestamp": timestamp,
            "scan_type": scan_type,
            "cyber_dna": cyber_dna
        }
        self._append_jsonl(self.dna_log_file, entry)
    
    def _update_daily_stats(self, scan_type: str, is_threat: bool):
        """Update daily statistics"""
        stats = self.get_daily_stats()
        
        # Increment counters
        stats["total_scans"] += 1
        stats["by_type"][scan_type] = stats["by_type"].get(scan_type, 0) + 1
        
        if is_threat:
            stats["threats_detected"] += 1
            stats["threats_by_type"][scan_type] = stats["threats_by_type"].get(scan_type, 0) + 1
        
        # Update timestamp
        stats["last_updated"] = datetime.utcnow().isoformat()
        
        # Write back
        with open(self.daily_stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats structure"""
        return {
            "date": datetime.utcnow().date().isoformat(),
            "total_scans": 0,
            "threats_detected": 0,
            "by_type": {},
            "threats_by_type": {},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _append_jsonl(self, file_path: Path, data: Dict):
        """Append JSON line to file"""
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    
    def _export_csv(self, output_path: Path, data: List[Dict], scan_type: str):
        """Export data as CSV"""
        import csv
        
        if not data:
            return
        
        # Define columns based on scan type
        if scan_type == "text":
            columns = ["scan_id", "timestamp", "raw_input", "threat_detected", 
                      "overall_confidence", "attack_goal", "dna_hash"]
        elif scan_type == "url":
            columns = ["scan_id", "timestamp", "raw_input", "threat_detected",
                      "overall_confidence", "attack_goal", "dna_hash"]
        else:  # image
            columns = ["scan_id", "timestamp", "threat_detected", 
                      "overall_confidence", "attack_goal", "dna_hash"]
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            
            for entry in data:
                row = {
                    "scan_id": entry.get("scan_id"),
                    "timestamp": entry.get("timestamp"),
                    "raw_input": entry.get("raw_input", ""),
                    "threat_detected": entry.get("threat_detected"),
                    "overall_confidence": entry.get("overall_confidence"),
                    "attack_goal": entry.get("redteam_analysis", {}).get("attack_goal", ""),
                    "dna_hash": entry.get("cyber_dna", {}).get("dna_hash", "")
                }
                writer.writerow(row)
