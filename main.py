from node import Node_Tree, Node
from datetime import datetime
from astral import LocationInfo


def main():
	city = LocationInfo("Polk City", "USA", "America/New_York", 28.19, -81.77)
	tree = Node_Tree(1.0, 0.66, 28800, datetime.now(), city)

if __name__ == "__main__":
	main()
