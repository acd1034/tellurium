from tellurium.arguments import make_from_arguments
from tellurium.make import BuildRule, run_rules

if __name__ == "__main__":
    run_rules(make_from_arguments(list[BuildRule]))
