# coding: utf-8
from typing import Dict, Any, List
import cv2
import numpy as np
from one_dragon.base.matcher.match_result import MatchResult
from one_dragon.utils import cv2_utils


class CvPipelineContext:
    """
    一个图像处理流水线的上下文
    """
    def __init__(self, source_image: np.ndarray, service: 'CvService' = None, debug_mode: bool = True):
        self.source_image: np.ndarray = source_image  # 原始输入图像 (只读)
        self.service: 'CvService' = service
        self.debug_mode: bool = debug_mode  # 是否为调试模式
        self.display_image: np.ndarray = source_image.copy()  # 用于UI显示的主图像，可被修改
        self.crop_offset: tuple[int, int] = (0, 0)  # display_image 左上角相对于 source_image 的坐标偏移
        self.mask_image: np.ndarray = None  # 二值掩码图像
        self.contours: List[np.ndarray] = []  # 检测到的轮廓列表
        self.analysis_results: List[str] = []  # 存储分析结果的字符串列表
        self.match_result: MatchResult = None
        self.ocr_result = None  # OcrResult from ocr step
        self.step_execution_times: list[tuple[str, float]] = []
        self.total_execution_time: float = 0.0
        self.error_str: str = None  # 致命错误信息
        self.success: bool = True  # 流水线逻辑是否成功

    @property
    def is_success(self) -> bool:
        """
        判断流水线是否执行成功
        :return:
        """
        return self.error_str is None and self.success

    @property
    def od_ctx(self) -> 'OneDragonContext':
        """
        通过service获取上下文
        :return:
        """
        return self.service.od_ctx if self.service else None

    @property
    def template_loader(self):
        return self.service.template_loader if self.service else None

    @property
    def ocr(self):
        return self.service.ocr if self.service else None


class CvStep:
    """
    所有图像处理步骤的基类
    """

    def __init__(self, name: str):
        self.name = name
        self.params: Dict[str, Any] = {}
        self._init_params()

    def _init_params(self):
        """
        使用默认值初始化参数
        """
        param_defs = self.get_params()
        for param_name, definition in param_defs.items():
            self.params[param_name] = definition.get('default')

    def get_params(self) -> Dict[str, Any]:
        """
        获取该步骤的所有可调参数及其定义
        :return:
        """
        return {}

    def to_dict(self) -> Dict[str, Any]:
        """
        将步骤转换为可序列化的字典
        """
        # 创建 params 的一个副本，并将元组转换为列表
        params_copy = {}
        for key, value in self.params.items():
            if isinstance(value, tuple):
                params_copy[key] = list(value)
            else:
                params_copy[key] = value

        return {
            'step': self.name,
            'params': params_copy
        }

    def update_from_dict(self, data: Dict[str, Any]):
        """
        从字典更新步骤的参数
        """
        param_defs = self.get_params()
        params_data = data.get('params', {})
        for param_name, value in params_data.items():
            if param_name in param_defs:
                # 如果定义的类型是元组，而加载的是列表，则进行转换
                if param_defs[param_name].get('type') == 'tuple_int' and isinstance(value, list):
                    self.params[param_name] = tuple(value)
                else:
                    self.params[param_name] = value

    def get_description(self) -> str:
        """
        获取该步骤的详细说明
        :return:
        """
        return ""

    def execute(self, context: CvPipelineContext, **kwargs):
        """
        执行处理步骤
        :param context: 流水线上下文
        """
        # 合并运行时参数和实例参数，运行时参数优先
        run_params = {**self.params, **kwargs}
        self._execute(context, **run_params)

    def _execute(self, context: CvPipelineContext, **kwargs):
        """
        子类需要重写的执行方法
        """
        pass

    def _crop_image_and_update_context(self, context: CvPipelineContext, rect, operation_name: str):
        """
        一个统一的裁剪方法，执行裁剪并更新上下文中的坐标偏移
        :param context: 流水线上下文
        :param rect: 裁剪区域
        :param operation_name: 用于日志记录的操作名称
        """
        if rect is None:
            context.error_str = f"错误: {operation_name} 的裁剪区域为空"
            context.success = False
            return

        context.display_image = cv2_utils.crop_image_only(context.display_image, rect)

        # 累加偏移量
        context.crop_offset = (context.crop_offset[0] + rect.x1, context.crop_offset[1] + rect.y1)

        context.analysis_results.append(f"已执行 {operation_name}，区域: {rect}，当前总偏移: {context.crop_offset}")

