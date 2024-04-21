from compress import *
from utils import *

def main():
    args = get_args()
    files = provide_files(args)
    if args['compress']:
        compress(files, 2147483648, args['rd'])
    elif args['decompress']:
        decompress(files, 2147483648)

if __name__ == "__main__":
    main()
