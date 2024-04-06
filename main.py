from compress import *

def main():
    args = get_args()
    if args['compress']:
        compress(args['filename'], 4096)
    elif args['decompress']:
        decompress(args['filename'], 4096)

if __name__ == "__main__":
    main()
