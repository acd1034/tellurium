from argparse import ArgumentParser

from .sample import square

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--square", type=int, default=2)
    args = parser.parse_args()
    print(square(args.square))
