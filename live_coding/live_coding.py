# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.01_depth_first


def depth_first():
    """Finds the lowest-cost simple path between start and target using backtracking."""



if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(depth_first(GRAPH, "S", "T"))
