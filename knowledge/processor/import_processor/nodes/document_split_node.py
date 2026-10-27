"""
文档切分节点（上）

按 Markdown 标题切分文档，本阶段实现参数校验和标题一级切分
"""

import re
from typing import Tuple, List
from knowledge.processor.import_processor.base import BaseNode, setup_logging
from knowledge.processor.import_processor.state import ImportGraphState
from knowledge.processor.import_processor.config import get_config


class DocumentSplitNode(BaseNode):
    """
    文档切分节点

    处理流程（本章部分）：
    1. 读取 MD 内容，校验参数
    2. 按 Markdown 标题进行一级切分（title 与 body 分离存储）
    """

    name = "document_split_node"

    # ------------------------------------------------------------------ #
    #                           主流程                                     #
    # ------------------------------------------------------------------ #

    def process(self, state: ImportGraphState) -> ImportGraphState:

        config = get_config()

        # 1. 获取参数
        md_content, file_title, max_content_length, min_content_length = self._validate_state(state, config)

        # 2. 根据标题切割(核心)
        sections = self._split_by_headings(md_content, file_title)

        # 8. 返回
        return state

    # ------------------------------------------------------------------ #
    #                       Step 1: 参数校验与获取                          #
    # ------------------------------------------------------------------ #

    def _validate_state(self, state: ImportGraphState, config) -> Tuple[str, str, int, int]:
        """获取输入参数并预处理"""
        self.log_step("step1", "切分文档的参数校验以及获取...")

        # 1. 获取md_content
        md_content = state.get('md_content')

        # 2. 统一换行符
        if md_content:
            md_content = md_content.replace("\r\n", "\n").replace("\r", "\n")

        # 3. 获取文件标题
        file_title = state.get('file_title')

        # 4. 校验最大最小值
        if config.max_content_length <= 0 or config.min_content_length <= 0 \
           or config.max_content_length <= config.min_content_length:
            raise ValueError(f"切片长度参数校验失败")

        return md_content, file_title, config.max_content_length, config.min_content_length

    # ------------------------------------------------------------------ #
    #                  Step 2: 按标题一级切分                               #
    # ------------------------------------------------------------------ #

    def _split_by_headings(self, md_content: str, file_title: str) -> List[dict]:
        """
        根据 MD 的标题（1-6）级标题进行切分

        Args:
            md_content: md内容
            file_title: 文档名字

        Returns:
            sections: 列表，每个元素格式：
            {
                "title": "# 第一章",
                "body": "正文内容...",
                "file_title": "万用表",
                "parent_title": "# 第一章"
            }
        """
        self.log_step("step2", "根据标题进行切分...")

        # 1. 定义变量
        in_fence = False
        body_lines = []
        sections = []
        current_level = 0
        current_title = ""  # 当前标题
        hierarchy = [""] * 7  # 7个长度，第一个（0）不用

        # 2. 定义正则表达式
        heading_re = re.compile(r"^\s*(#{1,6})\s+(.+)")

        # 3. 切分
        content_lines = md_content.split("\n")

        def _flush():
            """封装 section 对象"""
            body = "\n".join(body_lines)
            if current_title or body:
                parent_title = ""
                for i in range(current_level - 1, 0, -1):
                    if hierarchy[i]:
                        parent_title = hierarchy[i]
                        break

                if not parent_title:
                    parent_title = current_title if current_title else file_title

                return sections.append({
                    "title": current_title if current_title else file_title,
                    "body": body,
                    "file_title": file_title,
                    "parent_title": parent_title
                })

        for content_line in content_lines:
            # 判断是否存在代码块围栏
            if content_line.strip().startswith("```") or content_line.strip().startswith("~~~"):
                in_fence = not in_fence

            match = heading_re.match(content_line) if not in_fence else None

            if match:
                _flush()

                level = len(match.group(1))  # 当前标题的级别
                current_level = level
                current_title = content_line
                hierarchy[level] = current_title

                # 清空下级标题
                for i in range(level + 1, 7):
                    hierarchy[i] = ""

                body_lines = []
            else:
                # 除了标题行以外全都收集起来
                body_lines.append(content_line)

        _flush()

        return sections


if __name__ == '__main__':
    setup_logging()

    document_node = DocumentSplitNode()
    # 构造状态字典
    file_path = r"D:\develop\develop\workspace\pycharm\251020\shopkeeper_brain\docs\hybrid_auto\万用表的使用.md"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    state = {
        "file_title": "万用表的使用",
        "md_content": content,
        "file_dir": r"D:\develop\develop\workspace\pycharm\251020\shopkeeper_brain\knowledge\processor\import_process\import_temp_dir\万用表的使用\hybrid_auto"
    }
    document_node.process(state)