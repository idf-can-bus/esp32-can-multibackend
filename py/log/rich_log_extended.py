#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivo Marvan"
__email__ = "ivo@marvan.cz"
__description__ = '''   
Extended RichLog with buffering and performance optimizations.
Wraps standard RichLog to prevent GUI freezing during rapid output.
'''
from textual.widgets import RichLog
import time
import asyncio
from typing import Any, Optional

class RichLogExtended(RichLog):
    """
    Extended RichLog with buffering and performance optimizations.
    Wraps standard RichLog to prevent GUI freezing during rapid output.
    """
    def __init__(self, buffer_size: int = 10, flush_interval: float = 0.1, 
                 *args, **kwargs):
        # Předat max_lines do parent konstruktoru místo duplikace
        super().__init__(*args, **kwargs)
        
        # Buffering parameters
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.total_lines = 0
        self._last_flush = time.time()
        
        # Asyncio support
        self._async_lock = asyncio.Lock()
        
        # Statistics
        self.flush_count = 0
        self.total_flush_time = 0.0
        self.avg_flush_time = 0.0
        self.emergency_flush_count = 0

        self._flush_timer = None
    
    def write(self, content: Any, width: Optional[int] = None, 
              expand: bool = False, shrink: bool = True, 
              scroll_end: Optional[bool] = None, animate: bool = False) -> 'RichLogExtended':
        """
        Override write method with timer-based flushing
        """
        # Store original parameters
        write_params = {
            'content': content,
            'width': width,
            'expand': expand,
            'shrink': shrink,
            'scroll_end': scroll_end,
            'animate': animate
        }
        
        self.buffer.append(write_params)
        
        # Force flush on error messages
        content_str = str(content)
        if any(error_word in content_str.lower() for error_word in ['error', 'failed', 'exception', '❌']):
            self._flush_buffer()
            return self
        
        # Auto-throttling: emergency flush if buffer is too large
        if len(self.buffer) > self.buffer_size * 2:
            self.emergency_flush_count += 1
            self._flush_buffer()
            return self
        
        # Normal flush conditions
        if len(self.buffer) >= self.buffer_size:
            self._flush_buffer()
            return self
        
        # Start timer for interval-based flushing
        self._start_flush_timer()
        
        return self
    
    def _start_flush_timer(self):
        """
        Start timer for automatic flushing
        """
        # Cancel existing timer
        if self._flush_timer and not self._flush_timer.done():
            self._flush_timer.cancel()
        
        # Start new timer
        self._flush_timer = asyncio.create_task(self._timer_flush())
    
    async def _timer_flush(self):
        """
        Timer-based flush
        """
        await asyncio.sleep(self.flush_interval)
        
        # Check if buffer still has content
        if self.buffer:
            self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """
        Flush buffered content to actual RichLog
        """
        if not self.buffer:
            return
        
        # Cancel timer if running
        if self._flush_timer and not self._flush_timer.done():
            self._flush_timer.cancel()
        
        # Measure flush time
        flush_start = time.time()
        
        # Write all buffered content
        for write_params in self.buffer:
            super().write(**write_params)
            self.total_lines += 1
            
            # Line limiting using RichLog's built-in max_lines
            if self.max_lines and self.total_lines > self.max_lines:
                super().clear()
                self.total_lines = 0
        
        # Update statistics
        flush_time = time.time() - flush_start
        self.flush_count += 1
        self.total_flush_time += flush_time
        self.avg_flush_time = self.total_flush_time / self.flush_count
        
        # Clear buffer and update timestamp
        self.buffer.clear()
        self._last_flush = time.time()
    
    def clear(self) -> 'RichLogExtended':
        """Override clear to also clear buffer"""
        super().clear()
        self.buffer.clear()
        self.total_lines = 0
        return self  # Method chaining support
    
    def get_stats(self) -> dict:
        """Get performance statistics"""
        return {
            'total_lines': self.total_lines,
            'buffer_size': len(self.buffer),
            'flush_count': self.flush_count,
            'avg_flush_time': self.avg_flush_time,
            'emergency_flush_count': self.emergency_flush_count,
            'buffer_efficiency': self.flush_count / max(1, self.total_lines) if self.total_lines > 0 else 0
        }
    
    def print_stats(self) -> 'RichLogExtended':
        """Print statistics to the log"""
        stats = self.get_stats()
        self.write(f"📊 RichLogExtended Stats:")
        self.write(f"   Total lines: {stats['total_lines']}")
        self.write(f"   Flush count: {stats['flush_count']}")
        self.write(f"   Avg flush time: {stats['avg_flush_time']:.3f}s")
        self.write(f"   Emergency flushes: {stats['emergency_flush_count']}")
        self.write(f"   Buffer efficiency: {stats['buffer_efficiency']:.2f}")
        self._flush_buffer()
        return self