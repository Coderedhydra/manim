#!/usr/bin/env python3
"""
Demo script showing a sample Manim animation
This can be used to test if Manim is working properly
"""

from manim import *

class DemoScene(Scene):
    def construct(self):
        # Create title
        title = Text("Text to Manim Generator", font_size=48)
        title.set_color(BLUE)
        
        # Create subtitle
        subtitle = Text("AI-Powered Animation Creation", font_size=24)
        subtitle.set_color(GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Animate title
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(1)
        
        # Transform to welcome message
        welcome = Text("Welcome to the Future of Animation!", font_size=36)
        welcome.set_color(GREEN)
        
        self.play(
            Transform(title, welcome),
            FadeOut(subtitle)
        )
        self.wait(1)
        
        # Create shapes
        circle = Circle(radius=1, color=RED)
        square = Square(side_length=2, color=YELLOW)
        triangle = Triangle(color=PURPLE)
        
        # Position shapes
        circle.shift(LEFT * 3)
        square.shift(RIGHT * 3)
        triangle.shift(UP * 2)
        
        # Animate shapes
        self.play(
            Create(circle),
            Create(square),
            Create(triangle),
            FadeOut(welcome)
        )
        
        # Rotate shapes
        self.play(
            Rotate(circle, PI),
            Rotate(square, PI/2),
            Rotate(triangle, PI/3),
            run_time=2
        )
        
        # Final message
        final_text = Text("Ready to create amazing animations!", font_size=32)
        final_text.set_color(ORANGE)
        
        self.play(
            FadeOut(circle),
            FadeOut(square), 
            FadeOut(triangle),
            Write(final_text)
        )
        
        self.wait(2)

if __name__ == "__main__":
    # This allows the script to be run directly with: python demo_script.py
    import subprocess
    import sys
    
    print("🎬 Running demo animation...")
    print("This will create a sample video to test Manim installation")
    
    try:
        cmd = [
            'manim', 
            '-pql',  # Preview quality for faster rendering
            '--output_file', 'demo_output',
            sys.argv[0],  # This script file
            'DemoScene'
        ]
        
        result = subprocess.run(cmd, check=True)
        print("✅ Demo animation created successfully!")
        print("Check the media folder for the generated video.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Manim not found. Please install Manim first.")
        sys.exit(1)