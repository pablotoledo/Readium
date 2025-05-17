import sys

from .cli import main

if __name__ == "__main__":
    # Check if the 'tokens' command is used
    if len(sys.argv) > 1 and sys.argv[1] == "tokens":
        # Remove 'tokens' from argv and add --tokens
        sys.argv.pop(1)
        sys.argv.append("--tokens")
    main()
