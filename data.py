import json
from collections import defaultdict

with open("points.txt") as file:
    p = json.load(file)
    points = defaultdict(lambda: 5, p)

if __name__ == '__main__':
    print(points["biblock"])
    print(points["stan"])
