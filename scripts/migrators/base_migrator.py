#!/usr/bin/env python3

"""
Base migrator class for the Universal Logging Migrator.

This module provides the base class that all specific migrators inherit from,
as well as common utilities like the MigrationReport class.
"""

import os
import re
import json
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Union


class MigrationReport:
    """Class to track and report on migration changes."""
    
    def __init__(self):
        self.files_scanned = 0
        self.files_modified = 0
        self.changes = {}
        self.start_time = datetime.datetime.now()
    
    def add_change(self, file_path: str, change_type: str, old_text: str, new_text: str):
        """Add a change to the report."""
        if file_path not in self.changes:
            self.changes[file_path] = []
        
        self.changes[file_path].append({
            "type": change_type,
            "old": old_text,
            "new": new_text
        })
    
    def increment_scanned(self):
        """Increment the count of files scanned."""
        self.files_scanned += 1
    
    def increment_modified(self):
        """Increment the count of files modified."""
        self.files_modified += 1
    
    def generate_report(self) -> Dict:
        """Generate a report of all changes made."""
        end_time = datetime.datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            "summary": {
                "files_scanned": self.files_scanned,
                "files_modified": self.files_modified,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration
            },
            "changes": self.changes
        }
    
    def save_report(self, output_path: str):
        """Save the report to a JSON file."""
        report = self.generate_report()
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path


class BaseMigrator:
    """Base class for all migrators."""
    
    def __init__(self):
        self.name = "base"
        self.file_patterns = []
        self.dir_patterns = []
    
    def process_file(self, file_path: Path, report: MigrationReport, report_only: bool, verbose: bool) -> bool:
        """Process a file to migrate logging references.
        
        Args:
            file_path: Path to the file to process
            report: MigrationReport instance to track changes
            report_only: If True, don't make any changes, just report
            verbose: If True, print verbose output
            
        Returns:
            bool: True if the file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files or files with encoding issues
            return False
        
        report.increment_scanned()
        
        original_content = content
        modified = False
        
        # This should be implemented by subclasses
        new_content = self.migrate_content(content, file_path, report, verbose)
        
        if new_content != original_content:
            modified = True
            if not report_only:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                report.increment_modified()
                if verbose:
                    print(f"Updated file: {file_path}")
        
        return modified
    
    def migrate_content(self, content: str, file_path: Path, report: MigrationReport, verbose: bool) -> str:
        """Migrate logging references in the content.
        
        This method should be implemented by subclasses.
        
        Args:
            content: The content of the file
            file_path: Path to the file
            report: MigrationReport instance to track changes
            verbose: If True, print verbose output
            
        Returns:
            str: The updated content
        """
        return content  # By default, don't change anything
    
    def should_rename_file(self, file_name: str) -> bool:
        """Check if a file should be renamed.
        
        Args:
            file_name: Name of the file
            
        Returns:
            bool: True if the file should be renamed, False otherwise
        """
        for pattern in self.file_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                return True
        return False
    
    def get_renamed_file(self, file_name: str) -> str:
        """Get the new name for a file.
        
        This method should be implemented by subclasses if they have specific renaming logic.
        
        Args:
            file_name: Name of the file
            
        Returns:
            str: The new name for the file
        """
        return file_name  # By default, don't rename
    
    def should_rename_directory(self, dir_name: str) -> bool:
        """Check if a directory should be renamed.
        
        Args:
            dir_name: Name of the directory
            
        Returns:
            bool: True if the directory should be renamed, False otherwise
        """
        for pattern in self.dir_patterns:
            if re.search(pattern, dir_name, re.IGNORECASE):
                return True
        return False
    
    def get_renamed_directory(self, dir_name: str) -> str:
        """Get the new name for a directory.
        
        This method should be implemented by subclasses if they have specific renaming logic.
        
        Args:
            dir_name: Name of the directory
            
        Returns:
            str: The new name for the directory
        """
        return dir_name  # By default, don't rename
    
    def create_loglama_config(self, base_path: Path, report: MigrationReport, report_only: bool, verbose: bool):
        """Create LogLama configuration files based on existing logging configuration.
        
        This method should be implemented by subclasses if they have specific config creation logic.
        
        Args:
            base_path: Base path of the project
            report: MigrationReport instance to track changes
            report_only: If True, don't make any changes, just report
            verbose: If True, print verbose output
        """
        pass  # By default, do nothing
