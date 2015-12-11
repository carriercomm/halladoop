"""
Represents the "journal" of a filesystem similarly to what you'd expect int an ext# filesystem
#TODO
  - timestamps
"""
from threading import RLock

from namenode.image import config

lock = RLock()

class VirtualFileSystem:
    def __init__(self):
        self.root_inode = INode(config.DELIMITER, is_directory=True)
        self.data_nodes = {}

    def add_file(self, file_path): 
        self.__add_inode__(file_path, False) 

    def add_directory(self, file_path):
        self.__add_inode__(file_path, True)

    def __add_inode__(self, file_path, is_directory):
        with (yield from lock):
            print("made it")
            parent_inode = self.__parentinode__(file_path)
            if not parent_inode:
                self.add_directory(self.__parentpath__(file_path))
                parent_inode = self.__parentinode__(file_path)
            else:
                self.__check_parent_inode__(parent_inode)
    
            inode = INode(self.__filename__(file_path), is_directory)
            
            parent_inode.add_pointer(inode.file_name, inode)
        return inode        

    def add_block_entry(self, file_path, file_block_num, data_node_id):
        lock.acquire()
        with (yield from lock):
            inode = self.__get_inode__(file_path)
            if inode and not inode.is_directory:
                inode.add_pointer(file_block_num, data_node_id)
                self.__add_data_node_entry__(data_node_id, file_path, file_block_num)
            else:
                raise ValueError("INode at " + file_path + " either doesn't exist or isn't a file INode")

    def get_blocks_for_node(self, data_node_id):
        lock.acquire()
        lock.release()
        blocks = {}

        if data_node_id in self.data_nodes:
            blocks = self.data_nodes[data_node_id]

        return blocks

    def get_nodes_for_block(self, block_id):
        file_path, block_num = self.parse_block_id(block_id)
        inode = self.__get_inode__(file_path)

        nodes_with_block = set()
        if inode and block_num in inode.pointers:
            nodes_with_block.update(inode.pointers[block_num])

        return nodes_with_block

    def parse_block_id(self, block_id):
        file_name = block_id.split(config.DELIMITER)[-1]
        number_string = ""
        for char in reversed(file_name):
            if char.isdigit():
                number_string.append(char)
            else:
                break
        return int(reversed(number_string))

    def file_exists(self, file_path):
        return self.__get_inode__(file_path) is not None

    def __add_data_node_entry__(self, data_node_id, file_path, file_block_num):
        if data_node_id not in self.data_nodes:
            data_node_entries = set()
            self.data_nodes[data_node_id] = data_node_entries
        else:
            data_node_entries = self.data_nodes[data_node_id]

        block_id = file_path + str(file_block_num)

        if block_id not in data_node_entries:
            data_node_entries.add(block_id)

    def __get_inode__(self, file_path):
        lock.acquire()
        lock.release()
        current_node = self.root_inode
        dirs = list(filter(('').__ne__, file_path.split(config.DELIMITER)))
        for dir_name in dirs:
            if current_node.is_directory:
                if dir_name in current_node.pointers:
                    current_node = current_node.pointers[dir_name]
                else:
                    current_node = None
                    dirs.clear() # current_node doesn't exist, file_path not valid, break loop
            else:
                current_node = None
                dirs.clear() #stop loop

        return current_node

    def __filename__(self, file_path):
        return file_path.split(config.DELIMITER)[-1]

    def __parentinode__(self, file_path):
        parent_path = self.__parentpath__(file_path)
        return self.__get_inode__(parent_path)

    def __parentpath__(self, file_path):
        parent_dirs = []
        parent_dirs.extend(file_path.split(config.DELIMITER)[1:])
        parent_path = config.DELIMITER + config.DELIMITER.join(parent_dirs[:-1])
        return parent_path
        
    def __check_parent_inode__(self, parent_inode):
        if not parent_inode.is_directory:
            raise ValueError("Parent node is not a directory")  

#    def __str__(self):
#        return self

"""
A "pointer" is a dictionary for each INode such that
    INode is directory: key=child INode file name, value=child INode
    INode is not directory: key=block number, value=a DataNodePointer
"""
class INode:
    def __init__(self, file_name, is_directory=True, **pointers): 
        self.file_name = file_name
        self.is_directory = is_directory
        self.timestamp = None #TODO
        self.pointers = pointers

    def add_pointer(self, pointer_key, pointer_value):
        if pointer_key in self.pointers:
            if not self.is_directory:
                pointer = self.pointers[pointer_key]
                pointer.add(pointer_value)
        else:
            if self.is_directory:
                self.pointers[pointer_key] = pointer_value
            else:
                pointer = set([pointer_value])
                self.pointers[pointer_key] = pointer