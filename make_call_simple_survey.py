#!/usr/bin/env python3

import sys
import subprocess
import re
import os


def print_usage():
    print("Usage:")
    print("  python3 make_call.py <number> <source_number> <call_id>")
    print("")
    print("Examples:")
    print("  python3 make_call.py 1234567890 0546844668 1")
    print("")
    print("Arguments:")
    print("  number: The phone number to call")
    print("  source_number: The source phone number to use for the call")
    print("  call_id: The call ID to use")
    print("Number format: Any valid phone number")

def is_valid_number(number_str):
    """Check if the number looks like a valid phone number"""
    # Remove any non-digit characters
    clean_number = re.sub(r'\D', '', str(number_str))
    # Check if it's at least 7 digits (minimum for most phone numbers)
    return len(clean_number) >= 7

def normalize_number_asterisk(number_str):
    """
    Normalize a phone number string for Asterisk dialing.

    - Removes all non-digit characters.
    - If the number starts with the Israel country code "972", replace it with a leading "0".
    - If the number does not start with "0", prepend a leading "0".
    - Validate that the final normalized number starts with "05" (mobile prefix).

    Args:
        number_str (str): The input phone number to normalize.

    Returns:
        str: The normalized phone number (e.g., "05XXXXXXXX").

    Raises:
        ValueError: If the normalized number does not start with "05".
    """
    clean_number = re.sub(r'\D', '', number_str)
    if clean_number.startswith("972"):
        clean_number = "0" + clean_number[3:]
    elif clean_number.startswith("0"):
        pass
    else:
        clean_number = "0" + clean_number
    if not clean_number.startswith("05"):
        raise ValueError(f"Normalized number does not start with '05': {clean_number}")
    return clean_number

def clear_call_files(call_id):
    """Remove existing call files for the given call_id"""
    os.system(f"rm -f ./calls_answers/{call_id}_*")

def make_call(number, source_number, call_id):
    """Make an outgoing call using Asterisk call files"""
    try:
        if not source_number:
            print(f"❌ Error: Invalid source_number: {source_number}")
            return
        
        if not is_valid_number(source_number):
            print(f"❌ Error: Invalid source_number format: {source_number}")
            return

        number = normalize_number_asterisk(number)
        
        print(f"Making outgoing call to {number} via Simbank number {source_number}")

        cli_cmd = [
            "sudo", "-S", "asterisk", "-rx",
            f"channel originate Local/{source_number}-{number}-{call_id}@survey_example_player/n "
            f"extension {source_number}-{number}-{call_id}@survey_example_siptrunk"
        ]
        
        print(f"Originating call via CLI: {' '.join(cli_cmd)}")
        
        # Run sudo with empty password piped to stdin
        result = subprocess.run(cli_cmd, input="200334", capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Call originated successfully via Asterisk CLI")
            print(f"Output: {result.stdout}")
        else:
            print("❌ Failed to originate call")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # Check for help option
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_usage()
        sys.exit(0)
    
    if len(sys.argv) < 4:
        print("❌ Error: Missing arguments")
        print_usage()
        sys.exit(1)
    
    if len(sys.argv) > 4:
        print("❌ Error: Too many arguments")
        print_usage()
        sys.exit(1)
    
    # First argument is number (target), second is source_number, third is call_id
    number = sys.argv[1]
    source_number = sys.argv[2]
    call_id = sys.argv[3]
    
    # Validate inputs
    if not is_valid_number(number):
        print(f"❌ Error: Invalid target number '{number}'. Number must be at least 7 digits")
        sys.exit(1)
    
    if not is_valid_number(source_number):
        print(f"❌ Error: Invalid source number '{source_number}'. Number must be at least 7 digits")
        sys.exit(1)
    
    try:
        call_id_int = int(call_id)
        if call_id_int < 1:
            print(f"❌ Error: Invalid call_id '{call_id}'. Port must be a positive integer")
            sys.exit(1)
    except ValueError:
        print(f"❌ Error: Invalid call_id '{call_id}'. Port must be a valid integer")
        sys.exit(1)
    
    # Make the call
    make_call(number, source_number, call_id)

if __name__ == "__main__":
    main()
