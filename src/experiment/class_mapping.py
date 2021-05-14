superclass_mapping = {
    "beaver": "aquatic mammals",
    "dolphin": "aquatic mammals",
    "otter": "aquatic mammals",
    "seal": "aquatic mammals",
    "whale": "aquatic mammals",
    "aquarium_fish": "fish",
    "flatfish": "fish",
    "ray": "fish",
    "shark": "fish",
    "trout": "fish",
    "orchid": "flowers",
    "poppy": "flowers",
    "rose": "flowers",
    "sunflower": "flowers",
    "tulip": "flowers",
    "bottle": "food containers",
    "bowl": "food containers",
    "can": "food containers",
    "cup": "food containers",
    "plate": "food containers",
    "apple": "fruit and vegetables",
    "mushroom": "fruit and vegetables",
    "orange": "fruit and vegetables",
    "pear": "fruit and vegetables",
    "sweet_pepper": "fruit and vegetables",
    "clock": "household electrical devices",
    "keyboard": "household electrical devices",
    "lamp": "household electrical devices",
    "telephone": "household electrical devices",
    "television": "household electrical devices",
    "bed": "household furniture",
    "chair": "household furniture",
    "couch": "household furniture",
    "table": "household furniture",
    "wardrobe": "household furniture",
    "bee": "insects",
    "beetle": "insects",
    "butterfly": "insects",
    "caterpillar": "insects",
    "cockroach": "insects",
    "bear": "large carnivores",
    "leopard": "large carnivores",
    "lion": "large carnivores",
    "tiger": "large carnivores",
    "wolf": "large carnivores",
    "bridge": "large man-made outdoor things",
    "castle": "large man-made outdoor things",
    "house": "large man-made outdoor things",
    "road": "large man-made outdoor things",
    "skyscraper": "large man-made outdoor things",
    "cloud": "large natural outdoor scenes",
    "forest": "large natural outdoor scenes",
    "mountain": "large natural outdoor scenes",
    "plain": "large natural outdoor scenes",
    "sea": "large natural outdoor scenes",
    "camel": "large omnivores and herbivores",
    "cattle": "large omnivores and herbivores",
    "chimpanzee": "large omnivores and herbivores",
    "elephant": "large omnivores and herbivores",
    "kangaroo": "large omnivores and herbivores",
    "fox": "medium-sized mammals",
    "porcupine": "medium-sized mammals",
    "possum": "medium-sized mammals",
    "raccoon": "medium-sized mammals",
    "skunk": "medium-sized mammals",
    "crab": "non-insect invertebrates",
    "lobster": "non-insect invertebrates",
    "snail": "non-insect invertebrates",
    "spider": "non-insect invertebrates",
    "worm": "non-insect invertebrates",
    "baby": "people",
    "boy": "people",
    "girl": "people",
    "man": "people",
    "woman": "people",
    "crocodile": "reptiles",
    "dinosaur": "reptiles",
    "lizard": "reptiles",
    "snake": "reptiles",
    "turtle": "reptiles",
    "hamster": "small mammals",
    "mouse": "small mammals",
    "rabbit": "small mammals",
    "shrew": "small mammals",
    "squirrel": "small mammals",
    "maple_tree": "trees",
    "oak_tree": "trees",
    "palm_tree": "trees",
    "pine_tree": "trees",
    "willow_tree": "trees",
    "bicycle": "vehicles 1",
    "bus": "vehicles 1",
    "motorcycle": "vehicles 1",
    "pickup_truck": "vehicles 1",
    "train": "vehicles 1",
    "lawn_mower": "vehicles 2",
    "rocket": "vehicles 2",
    "streetcar": "vehicles 2",
    "tank": "vehicles 2",
    "tractor": "vehicles 2",
}


super_class_label = {
    "aquatic mammals": 0,
    "fish": 1,
    "flowers": 2,
    "food containers": 3,
    "fruit and vegetables": 4,
    "household electrical devices": 5,
    "household furniture": 6,
    "insects": 7,
    "large carnivores": 8,
    "large man-made outdoor things": 9,
    "large natural outdoor scenes": 10,
    "large omnivores and herbivores": 11,
    "medium-sized mammals": 12,
    "non-insect invertebrates": 13,
    "people": 14,
    "reptiles": 15,
    "small mammals": 16,
    "trees": 17,
    "vehicles 1": 18,
    "vehicles 2": 19,
}


seen_sc_labels = {}
hierarchical_label_structure = {}
for i, (label, sc_label) in enumerate(superclass_mapping.items()):
    if sc_label not in seen_sc_labels:
        seen_sc_labels[sc_label] = 0
    hierarchical_label_structure[label] = (super_class_label[sc_label], seen_sc_labels[sc_label])
    seen_sc_labels[sc_label] += 1


cifar_10_mapping = {
    "airplane": "inanimate",
    "automobile": "inanimate",
    "bird": "animate",
    "cat": "animate",
    "deer": "animate",
    "dog": "animate",
    "frog": "animate",
    "horse": "animate",
    "ship": "inanimate",
    "truck": "inanimate",
}


mnist_domain_knowledge = {
    0: [[0, 0]],
    1: [[0, 1], [1, 0]],
    2: [[0, 2], [1, 1], [2, 0]],
    3: [[0, 3], [1, 2], [2, 1], [3, 0]],
    4: [[0, 4], [1, 3], [2, 2], [3, 1], [4, 0]],
    5: [[0, 5], [1, 4], [2, 3], [3, 2], [4, 1], [5, 0]],
    6: [[0, 6], [1, 5], [2, 4], [3, 3], [4, 2], [5, 1], [6, 0]],
    7: [[0, 7], [1, 6], [2, 5], [3, 4], [4, 3], [5, 2], [6, 1], [7, 0]],
    8: [[0, 8], [1, 7], [2, 6], [3, 5], [4, 4], [5, 3], [6, 2], [7, 1], [8, 0]],
    9: [[0, 9], [1, 8], [2, 7], [3, 6], [4, 5], [5, 4], [6, 3], [7, 2], [8, 1], [9, 0]],
    10: [[1, 9], [2, 8], [3, 7], [4, 6], [5, 5], [6, 4], [7, 3], [8, 2], [9, 1]],
    11: [[2, 9], [3, 8], [4, 7], [5, 6], [6, 5], [7, 4], [8, 3], [9, 2]],
    12: [[3, 9], [4, 8], [5, 7], [6, 6], [7, 5], [8, 4], [9, 3]],
    13: [[4, 9], [5, 8], [6, 7], [7, 6], [8, 5], [9, 4]],
    14: [[5, 9], [6, 8], [7, 7], [8, 6], [9, 5]],
    15: [[6, 9], [7, 8], [8, 7], [9, 6]],
    16: [[7, 9], [8, 8], [9, 7]],
    17: [[8, 9], [9, 8]],
    18: [[9, 9]],
}

flat_class_mapping = [(l1, l2, k) for k, ls in mnist_domain_knowledge.items() for l1, l2 in ls]