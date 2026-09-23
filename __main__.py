# entrada del programa nomas
try:
    from .entrada import main
except ImportError:
    from entrada import main


if __name__ == "__main__":
    main()
