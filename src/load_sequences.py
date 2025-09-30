from pathlib import Path

def load_sequences(folder: Path):
    """
    Load state index sequences from all `.txt` files in a folder.

    Each text file is expected to contain one integer per line,
    representing the index of the chord/state to be played at that step.

    Args:
        folder (Path): Path to the folder containing `.txt` sequence files.

    Returns:
        Dict[str, List[int]]: A dictionary mapping the filename (without extension)
        to its corresponding sequence of integers.
    """
    sequences = {}

    for file in folder.glob("*.txt"):
        with open(file, encoding="utf-8") as f:
            seq = [int(line.strip()) for line in f if line.strip()]
        sequences[file.stem] = seq # use filename without extension as key

    return sequences
