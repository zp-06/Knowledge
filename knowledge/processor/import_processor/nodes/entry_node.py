from pathlib import Path

from knowledge.processor.import_processor.base import BaseNode, T
from knowledge.processor.import_processor.exceptions import ValidationError, StateFieldError
from knowledge.processor.import_processor.state import ImportGraphState

"""
判断上传的文件是否存在，以及文件、目录是否真实存在，根据文件后缀修改state中 is_md_read_enabled  is_pdf_read_enabled            
"""
class EntryNode(BaseNode):
    name = "entry_node"
    def process(self, state: ImportGraphState) -> ImportGraphState:
        #1. 获取上传文件路径
        import_file_path = state.get("import_file_path")
        file_dir = state.get("file_dir")

        #2. 判断是否存在
        if not import_file_path:
            raise ValidationError(message="import_file_path不能为空", node_name=self.name)
        if not file_dir:
            raise ValidationError(message="file_dir不能为空", node_name=self.name)

        #3. 判断文件、以及目录是否真实存在
        import_file_path_obj = Path(import_file_path)
        file_dir_obj = Path(file_dir)

        if not import_file_path_obj.exists():
            raise StateFieldError(node_name=self.name, field_name="import_file_path_obj", expected_type=Path)

        if not file_dir_obj.exists():
            raise StateFieldError(node_name=self.name, field_name="file_dir_obj", expected_type=Path)

        #4. 根据文件的后缀，修改state中 is_md_read_enabled  is_pdf_read_enabled
        if import_file_path_obj.suffix == ".pdf":
            state["is_pdf_read_enabled"] = True
            state["pdf_path"] = str(import_file_path_obj)
        elif import_file_path_obj.suffix == ".md":
            state["is_md_read_enabled"] = True
            state["md_path"] = str(import_file_path_obj)
        else:
            self.logger.error(f"该文件后缀格式{import_file_path_obj.suffix}不支持")
            raise ValidationError(message=f"该文件的后缀格式{import_file_path_obj.suffix}不支持", node_name=self.name)

        #5. 获取文件标题(不包含后缀),并设置到state中
        state['file_title'] = import_file_path_obj.stem

        return state

if __name__ == '__main__':
    entry_node = EntryNode()
    init_state = {
        "import_file_path": r"D:\BaiduNetdiskDownload\新建文件夹 (2)\09-尚硅谷Java智能项目之掌柜智库\资料包\pdf文档\doc\Aolynk CB304n Cable网桥 用户手册-5W100-整本手册.pdf",
        "file_dir": r"D:\my_study\my_study_of_py\zhiku\knowledge\processor\import_processor\nodes\output"
    }
    result_state = entry_node(init_state)
    print(result_state)