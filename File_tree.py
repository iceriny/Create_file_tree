import os
from typing import Optional, Union
import warnings


# 自定义异常类，表示路径不存在
class PathNotExists(Exception):
    pass


# FileTree类表示一个文件夹及其包含的文件和子文件夹的树状结构
class FileTree:

    def __init__(
        self,
        name: str,
        parent: "str | FileTree",
        *,
        files: Union[dict[str, str], None] = None,
        children: Union[str, "FileTree", None] = None,
    ):
        """
        初始化FileTree实例。

        :param name: 文件夹的名称
        :param parent: 父级目录的路径或FileTree对象
        :param files: 当前文件夹包含的文件名和内容的字典
        :param children: 当前文件夹的子文件夹，可为路径、FileTree对象或None
        :raises ValueError: 如果父级目录路径不存在则抛出异常
        """
        if isinstance(parent, str) and not os.path.exists(parent):
            warnings.warn(
                f"Root node root path not exists: {parent}",
                stacklevel=2,
            )
        self.parent: str | FileTree = parent
        self.name: str = name
        if children is not None:
            self.add_child(*children)
        else:
            self.children: dict[str, FileTree] = {}
        self.files: dict[str, str] = files or {}

    def _repr_helper(self, indent: int = 0) -> str:
        indent_str = "    " * indent
        repr_str = f"{indent_str}<FileTree(name='{self.name}')\n"

        # 添加子节点
        if self.children:
            repr_str += f"{indent_str}  Children:\n"
            for child in self.children.values():
                repr_str += child._repr_helper(indent + 2)
        return repr_str

    def __repr__(self) -> str:
        return self._repr_helper()

    def __str__(self) -> str:
        return self.get_path()

    def get_file_content(self, file_name: str) -> Optional[str]:
        """
        获取文件内容。

        :param file_name: 文件名
        :return: 文件内容，如果文件不存在则返回None
        """
        return self.files.get(file_name)

    def get_file_path(self, file_name: str) -> Optional[str]:
        """
        获取文件的完整路径。

        :param file_name: 文件名
        :return: 文件的完整路径，如果文件不存在则返回None
        """
        file_item = self.files.get(file_name)
        if file_item is None:
            return None

        return os.path.join(self.get_path(), file_name)

    def __get_path_recursive(self, path: str = "") -> str:
        """
        递归获取当前文件夹的完整路径。

        :param path: 当前路径
        :return: 完整路径
        """
        if isinstance(self.parent, str):
            return os.path.join(self.parent, self.name, path)
        else:
            path = os.path.join(self.name, path)
            return self.parent.__get_path_recursive(path)

    def get_path(self) -> str:
        """
        获取当前文件夹的完整路径。

        :return: 完整路径
        """
        return self.__get_path_recursive()

    def get_root_path(self) -> str:
        """
        获取根目录的路径。

        :return: 根目录的路径
        """
        if not isinstance(self.parent, str):
            return self.parent.get_root_path()
        else:
            return self.parent

    def get_root(self) -> "FileTree":
        """
        获取根目录的FileTree对象。

        :return: 根目录的FileTree对象
        """
        return self if isinstance(self.parent, str) else self.parent.get_root()

    def get_child(self, name: str) -> "FileTree | None":
        return self.children.get(name)

    def create_file(self, file_name: str, encoding: str = "utf-8"):
        """
        创建物理文件。

        :param file_name: 文件名
        :param encoding: 文件编码，默认为utf-8
        :raises FileNotFoundError: 如果虚拟文件不存在于当前节点下，则抛出文件未找到异常
        :raises PathNotExists: 如果路径不存在，则抛出路径不存在异常
        """
        pass
        file_path = self.get_file_path(file_name)
        if not file_path:
            raise FileNotFoundError(
                f"Virtual file {file_name} not found from node {self.name}"
            )
        try:
            with open(file_path, "w", encoding=encoding) as f:
                f.write(self.files[file_name])
        except Exception as e:
            raise PathNotExists(f"Maybe path {self.get_path()} not exists", e)

    def __mkdir__(self) -> None:
        """
        递归创建当前节点及其子节点的目录结构。
        """
        os.mkdir(self.get_path())
        for child in self.children.values():
            child.__mkdir__()

    def mkdir(self) -> None:
        """
        创建根目录及其子目录的目录结构。
        """
        self.get_root().__mkdir__()

    def __mkTree__(self) -> None:
        """
        递归创建当前节点及其子节点的文件树，包括文件和目录。
        """
        os.mkdir(path=self.get_path())
        for file_name in self.files.keys():
            self.create_file(file_name)

        for child in self.children.values():
            child.__mkTree__()

    def mkTree(self) -> None:
        """
        创建根目录及其子目录的文件树，包括文件和目录。
        """
        self.get_root().__mkTree__()

    def add_file(self, **files: str) -> None:
        """
        添加文件到当前文件夹。

        :param files: 文件名和内容的键值对
        """
        for name, content in files.items():
            self.files[name] = content

    def add_child(self, *child: Union[str, "FileTree"]) -> None:
        """
        添加子文件夹到当前文件夹。

        :param child: 子文件夹的名称或FileTree对象
        """
        for c in child:
            if isinstance(c, str):
                self.children[c] = FileTree(c, self)
            else:
                c.parent = self
                self.children[c.name] = c
