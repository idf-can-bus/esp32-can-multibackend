#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal test for character-by-character writing to RichLog.
Tests if it's possible to write individual characters with time delays.
"""

import asyncio
import time
from textual.app import App, ComposeResult
from textual.widgets import Log, Button, Header, Footer


class LogMinimalApp(App):
    """Minimal app to test character-by-character RichLog writing."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Log(id="test-log")
        yield Button("Start Test", id="start-button")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-button":
            event.button.disabled = True
            event.button.text = "Running..."
            self.run_worker(self.test_character_streaming())
    
    async def test_character_streaming(self) -> None:
        """Test writing characters one by one with delays."""
        log = self.query_one("#test-log", Log)
        
        # Test string to stream
        test_string = "[FAKE] ESP32 boot sequence started...\n"
        
        log.write("=== Character-by-character streaming test ===\n")
        log.write("Streaming: ")
        
        # Write each character with delay
        log.write("Write each character with delay:\n")
        for char in test_string:
            log.write(char)
            await asyncio.sleep(0.3)  # 300ms delay between characters

        log.write("Write more rows for scrolling test:\n")
        for i in range(50):
            log.write(f"Line {i+1}: \n")
            await asyncio.sleep(0.1)
        
        log.write("\n=== Test completed ===\n")
        
        # Re-enable button
        button = self.query_one("#start-button", Button)
        button.disabled = False
        button.text = "Start Test"


if __name__ == "__main__":
    app = LogMinimalApp()
    app.run()
