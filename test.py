import os
import sys
from File_tree import FileTree

path = os.path.abspath(os.path.dirname(__file__))

root = FileTree("test_folder", path)

root.add_file(**{"test.txt": "Hello World!"})

root.add_child("test_folder2")

folder2_node = root.get_child("test_folder2")
if folder2_node:
    folder3_node = FileTree("test_folder3", path)
    folder2_node.add_child(folder3_node)
    folder3_node.add_file(**{"test3.txt": "Hello World!"})

print(root)
# root.mkTree()
