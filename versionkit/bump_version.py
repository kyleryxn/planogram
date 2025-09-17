if __name__ == "__main__":
    # If executed as a package module: python -m versionkit.bump_version
    if __package__:
        from .cli import main
    else:
        # Executed directly: python versionkit/bump_version.py
        # Make relative imports work when __package__ is empty
        import os, sys
        sys.path.insert(0, os.path.dirname(__file__))
        from cli import main

    main()
