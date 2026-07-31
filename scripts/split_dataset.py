from pathlib import Path
import shutil
import random

PROJECT_ROOT = Path(__file__).resolve().parent.parent

NORMAL_DIR = PROJECT_ROOT / "data" / "normal"
ANOMALOUS_DIR = PROJECT_ROOT / "data" / "anomalous"

OUTPUT = PROJECT_ROOT / "data"

TRAIN = 0.70
VAL = 0.15
TEST = 0.15

SEED = 42

random.seed(SEED)


def split_files(files):

    random.shuffle(files)

    n = len(files)

    n_train = int(TRAIN * n)
    n_val = int(VAL * n)

    train = files[:n_train]
    val = files[n_train:n_train + n_val]
    test = files[n_train + n_val:]

    return train, val, test


def copy(files, destination):

    destination.mkdir(parents=True, exist_ok=True)

    for f in files:
        shutil.copy2(f, destination / f.name)


def main():

    normal_files = list(NORMAL_DIR.glob("*.json"))
    anomaly_files = list(ANOMALOUS_DIR.glob("*.json"))

    train_normal, val_normal, test_normal = split_files(normal_files)

    _, val_anomaly, test_anomaly = split_files(anomaly_files)

    copy(train_normal, OUTPUT / "train" / "normal")

    copy(val_normal, OUTPUT / "val" / "normal")
    copy(val_anomaly, OUTPUT / "val" / "anomalous")

    copy(test_normal, OUTPUT / "test" / "normal")
    copy(test_anomaly, OUTPUT / "test" / "anomalous")

    print("Dataset created")

    print(f"Train normal : {len(train_normal)}")

    print(f"Validation normal : {len(val_normal)}")
    print(f"Validation anomaly : {len(val_anomaly)}")

    print(f"Test normal : {len(test_normal)}")
    print(f"Test anomaly : {len(test_anomaly)}")


if __name__ == "__main__":
    main()