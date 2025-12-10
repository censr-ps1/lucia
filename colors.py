"""
A simple color utility module for adding ANSI colors to terminal output.
Uses 24-bit "true color" escape codes for a modern look.
NOTE: Assumes the terminal running this supports ANSI color codes.
"""

import sys

# 24-bit "True Color" (RGB) escape codes
# \33[38;2;R;G;Bm  <- Foreground
# \33[1m           <- Bold
# \33[0m           <- Reset all
COLORS = {
    # --- Modifiers ---
    "ENDC": "\33[0m",
    "RESET": "\33[0m",
    "BOLD": "\33[1m",
    "UNDERLINE": "\33[4m",
    
    # System/Info messages (Bright Cyan)
    "SYSTEM": "\33[38;2;102;217;255m",
    # Alias for SYSTEM
    "INFO": "\33[38;2;102;217;255m",

    # Received messages (Bright Magenta/Violet)
    "RECEIVED": "\33[38;2;204;153;255m",
    
    # User prompt (Light Grey)
    "PROMPT": "\33[38;2;180;180;180m",
    
    # --- Status Colors ---
    
    # Success (Minty Green)
    "SUCCESS": "\33[38;2;102;255;178m",
    
    # Warning (Amber/Yellow)
    "WARNING": "\33[38;2;255;199;0m",
    
    # Error (Bright, light Red)
    "ERROR": "\33[38;2;255;102;102m",

    # --- Basic Colors (for reference) ---
    "BLACK": "\33[38;2;0;0;0m",
    "WHITE": "\33[38;2;255;255;255m",
}

def cstr(text: str, color_key: str = "SYSTEM") -> str:
    """
    Returns a text string wrapped in the specified color codes.
    Does NOT print.
    
    Args:
        text (str): The text to colorize.
        color_key (str): The key from the COLORS dictionary (e.g., "ERROR").
    
    Returns:
        str: The color-wrapped string.
    """
    # Get the color code, default to empty string if key is invalid
    color_code = COLORS.get(color_key.upper(), "")
    end_code = COLORS['ENDC']
    return f"{color_code}{text}{end_code}"

def cprint(text: str, color_key: str = "SYSTEM", **kwargs):
    """
    Prints text in a color.
    Accepts all standard print() keyword arguments (like 'end', 'file').
    
    Args:
        text (str): The text to print.
        color_key (str): The key from the COLORS dictionary (e.g., "ERROR").
        **kwargs: Additional args for the built-in print() function.
    """
    print(cstr(text, color_key), **kwargs)

#Convenience Functions cause my ass is not using all those parameters

def print_error(text: str, **kwargs):
    """Shortcut for cprint(text, "ERROR")"""
    cprint(text, "ERROR", **kwargs)

def print_warning(text: str, **kwargs):
    """Shortcut for cprint(text, "WARNING")"""
    cprint(text, "WARNING", **kwargs)

def print_success(text: str, **kwargs):
    """Shortcut for cprint(text, "SUCCESS")"""
    cprint(text, "SUCCESS", **kwargs)

def print_info(text: str, **kwargs):
    """Shortcut for cprint(text, "INFO")"""
    cprint(text, "INFO", **kwargs)

def print_received(text: str, **kwargs):
    """Shortcut for cprint(text, "RECEIVED")"""
    cprint(text, "RECEIVED", **kwargs)

def get_prompt(text: str) -> str:
    """
    Returns a colorized string ideal for an input() prompt.
    This ensures the user's typing is in the default color.
    
    Args:
        text (str): The prompt text (e.g., ">> ").
    
    Returns:
        str: The colorized prompt string.
    """
    return cstr(text, "PROMPT")

# Demo
def _demo_colors():
    """Prints a demo of all available colors and styles."""
    
    print("--- Color Demo ---")
    
    # Test convenience functions
    print_error("This is an ERROR message.")
    print_warning("This is a WARNING message.")
    print_success("This is a SUCCESS message.")
    print_info("This is an INFO/SYSTEM message.")
    print_received("This is a RECEIVED message.")
    
    # Test cprint and kwargs
    cprint("This is a PROMPT", "PROMPT", end="")
    print(" (with no newline)")
    
    # Test cstr
    bold_white = cstr(cstr("This is BOLD and WHITE", "WHITE"), "BOLD")
    print(bold_white)
    
    # Test input prompt
    print("\n--- Prompt Demo ---")
    print("The next line is a colored prompt. Your typing should be normal.")
    try:
        # get_prompt() is used INSIDE the input()
        name = input(get_prompt("Enter your name >> "))
        print_success(f"Hello, {name}!")
    except EOFError:
        pass

if __name__ == "__main__":
    _demo_colors()

