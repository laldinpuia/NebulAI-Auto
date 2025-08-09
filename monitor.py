#!/usr/bin/env python3
"""
NebulAI Mining Performance Monitor
Displays real-time statistics from the mining log file
"""

import time
import os
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import curses

class MiningMonitor:
    def __init__(self, log_file: str = "nebulai_miner.log"):
        self.log_file = log_file
        self.stats = defaultdict(lambda: {"success": 0, "failure": 0, "last_seen": None})
        self.overall_stats = {"total_success": 0, "total_failure": 0, "start_time": time.time()}
        self.last_position = 0
        
    def parse_log_line(self, line: str) -> Tuple[str, str, str]:
        """Parse a log line for relevant information"""
        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        timestamp = timestamp_match.group(1) if timestamp_match else ""
        
        # Extract token (first 8 chars)
        token_match = re.search(r'for ([a-zA-Z0-9]{8})\.\.\.', line)
        token = token_match.group(1) if token_match else ""
        
        # Determine event type
        if "Results accepted" in line or "[✅]" in line:
            event = "success"
        elif "Results rejected" in line or "[❌]" in line:
            event = "failure"
        elif "Task received" in line or "[📥]" in line:
            event = "task_received"
        elif "Token refreshed" in line or "[🔄]" in line:
            event = "token_refreshed"
        else:
            event = "other"
            
        return timestamp, token, event
    
    def update_stats(self):
        """Update statistics from log file"""
        if not os.path.exists(self.log_file):
            return
            
        try:
            with open(self.log_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                
            for line in new_lines:
                timestamp, token, event = self.parse_log_line(line)
                
                if token and event in ["success", "failure"]:
                    self.stats[token][event] += 1
                    self.stats[token]["last_seen"] = timestamp
                    
                    if event == "success":
                        self.overall_stats["total_success"] += 1
                    else:
                        self.overall_stats["total_failure"] += 1
                        
        except Exception as e:
            pass  # Silently handle errors in monitoring
    
    def get_success_rate(self, token: str) -> float:
        """Calculate success rate for a token"""
        stats = self.stats[token]
        total = stats["success"] + stats["failure"]
        return (stats["success"] / total * 100) if total > 0 else 0
    
    def get_overall_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = self.overall_stats["total_success"] + self.overall_stats["total_failure"]
        return (self.overall_stats["total_success"] / total * 100) if total > 0 else 0
    
    def format_uptime(self) -> str:
        """Format uptime as human-readable string"""
        uptime = time.time() - self.overall_stats["start_time"]
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def draw_dashboard(stdscr, monitor: MiningMonitor):
    """Draw the monitoring dashboard using curses"""
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    
    # Color pairs
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    while True:
        try:
            # Update statistics
            monitor.update_stats()
            
            # Clear screen
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Header
            header = "🚀 NebulAI Mining Monitor 🚀"
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD | curses.color_pair(4))
            
            # Warning
            warning = "⚠️  WARNING: This violates NebulAI ToS! ⚠️"
            stdscr.addstr(1, (width - len(warning)) // 2, warning, curses.color_pair(3))
            
            # Overall statistics
            y = 3
            stdscr.addstr(y, 2, "━" * (width - 4), curses.A_DIM)
            y += 1
            stdscr.addstr(y, 2, "OVERALL STATISTICS", curses.A_BOLD)
            y += 1
            
            uptime = monitor.format_uptime()
            overall_rate = monitor.get_overall_success_rate()
            
            stdscr.addstr(y, 2, f"Uptime: {uptime}")
            stdscr.addstr(y, 25, f"Success: {monitor.overall_stats['total_success']}", curses.color_pair(1))
            stdscr.addstr(y, 45, f"Failure: {monitor.overall_stats['total_failure']}", curses.color_pair(2))
            stdscr.addstr(y, 65, f"Rate: {overall_rate:.1f}%", 
                         curses.color_pair(1) if overall_rate > 80 else curses.color_pair(2))
            
            # Per-token statistics
            y += 2
            stdscr.addstr(y, 2, "━" * (width - 4), curses.A_DIM)
            y += 1
            stdscr.addstr(y, 2, "PER-TOKEN STATISTICS", curses.A_BOLD)
            y += 2
            
            # Table header
            stdscr.addstr(y, 2, "Token", curses.A_UNDERLINE)
            stdscr.addstr(y, 15, "Success", curses.A_UNDERLINE)
            stdscr.addstr(y, 28, "Failure", curses.A_UNDERLINE)
            stdscr.addstr(y, 40, "Rate", curses.A_UNDERLINE)
            stdscr.addstr(y, 50, "Last Seen", curses.A_UNDERLINE)
            y += 1
            
            # Token data
            for token, stats in sorted(monitor.stats.items()):
                if y >= height - 3:  # Leave room for footer
                    break
                    
                success_rate = monitor.get_success_rate(token)
                color = curses.color_pair(1) if success_rate > 80 else curses.color_pair(2)
                
                stdscr.addstr(y, 2, f"{token}...")
                stdscr.addstr(y, 15, str(stats["success"]), curses.color_pair(1))
                stdscr.addstr(y, 28, str(stats["failure"]), curses.color_pair(2))
                stdscr.addstr(y, 40, f"{success_rate:.1f}%", color)
                stdscr.addstr(y, 50, stats["last_seen"] or "Never")
                y += 1
            
            # Footer
            stdscr.addstr(height - 2, 2, "━" * (width - 4), curses.A_DIM)
            footer = "Press 'q' to quit | Updates every 2 seconds"
            stdscr.addstr(height - 1, (width - len(footer)) // 2, footer, curses.A_DIM)
            
            # Refresh display
            stdscr.refresh()
            
            # Check for quit command
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
                
            # Update every 2 seconds
            time.sleep(2)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            # Handle resize and other errors gracefully
            pass

def main():
    """Main entry point"""
    print("Starting NebulAI Mining Monitor...")
    print("Press 'q' to quit")
    time.sleep(1)
    
    monitor = MiningMonitor()
    
    try:
        curses.wrapper(draw_dashboard, monitor)
    except KeyboardInterrupt:
        pass
    
    print("\nMonitoring stopped.")
    
    # Print final statistics
    print(f"\nFinal Statistics:")
    print(f"Total Runtime: {monitor.format_uptime()}")
    print(f"Total Success: {monitor.overall_stats['total_success']}")
    print(f"Total Failure: {monitor.overall_stats['total_failure']}")
    print(f"Overall Success Rate: {monitor.get_overall_success_rate():.1f}%")

if __name__ == "__main__":
    main()