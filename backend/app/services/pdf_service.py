"""PDF 文件处理服务"""
import re
from datetime import datetime
from typing import Optional, Dict, Any
import pdfplumber
from pathlib import Path


class PDFService:
    """PDF 文件处理服务"""

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        从 PDF 文件中提取文本

        Args:
            pdf_path: PDF 文件路径

        Returns:
            提取的文本内容
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"PDF 文本提取失败: {str(e)}")

        return text.strip()

    @staticmethod
    def parse_case_info(text: str) -> Dict[str, Any]:
        """
        从文本中解析案件信息

        Args:
            text: 案件文本内容

        Returns:
            解析出的案件信息
        """
        info = {
            "case_number": None,
            "title": None,
            "court": None,
            "case_type": None,
            "judgment_date": None,
            "parties": {},
        }

        # 提取案号（支持多种格式）
        case_number_patterns = [
            r'\(\d{4}\)[\u4e00-\u9fa5]{1,10}\d+[\u4e00-\u9fa5]{1,10}\d+号',  # (2023)京01民终1234号
            r'[（(]\d{4}[）)][\u4e00-\u9fa5]{1,10}\d+号',  # (2023)京民终1234号
            r'案号[：:]\s*([（(]\d{4}[）)][\u4e00-\u9fa5]{1,10}\d+号)',
        ]
        for pattern in case_number_patterns:
            match = re.search(pattern, text)
            if match:
                info["case_number"] = match.group(0) if '案号' not in match.group(0) else match.group(1)
                break

        # 提取标题（通常在开头）
        title_patterns = [
            r'([\u4e00-\u9fa5]+诉[\u4e00-\u9fa5]+.{0,50}?[案纠纷]{1,3})',
            r'([\u4e00-\u9fa5]{2,10}与[\u4e00-\u9fa5]{2,10}.{0,50}?[案纠纷]{1,3})',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text[:500])
            if match:
                info["title"] = match.group(1)
                break

        # 提取法院
        court_patterns = [
            r'([\u4e00-\u9fa5]{2,15}人民法院)',
            r'审理法院[：:]\s*([\u4e00-\u9fa5]{2,15}人民法院)',
        ]
        for pattern in court_patterns:
            match = re.search(pattern, text[:1000])
            if match:
                info["court"] = match.group(1) if '审理法院' not in match.group(0) else match.group(1)
                break

        # 提取案件类型
        if '民事' in text[:500]:
            info["case_type"] = "民事"
        elif '刑事' in text[:500]:
            info["case_type"] = "刑事"
        elif '行政' in text[:500]:
            info["case_type"] = "行政"

        # 提取判决日期
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'判决日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    info["judgment_date"] = datetime(year, month, day).date()
                    break
                except:
                    pass

        # 提取当事人（简单版本）
        plaintiff_match = re.search(r'原告[：:]\s*([\u4e00-\u9fa5]{2,10})', text[:2000])
        if plaintiff_match:
            info["parties"]["plaintiff"] = [plaintiff_match.group(1)]

        defendant_match = re.search(r'被告[：:]\s*([\u4e00-\u9fa5]{2,10})', text[:2000])
        if defendant_match:
            info["parties"]["defendant"] = [defendant_match.group(1)]

        return info

    @staticmethod
    def validate_pdf(file_path: str, max_size_mb: int = 10) -> tuple[bool, Optional[str]]:
        """
        验证 PDF 文件

        Args:
            file_path: 文件路径
            max_size_mb: 最大文件大小（MB）

        Returns:
            (是否有效, 错误信息)
        """
        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            return False, "文件不存在"

        # 检查文件大小
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"文件大小超过限制（{max_size_mb}MB）"

        # 检查是否为有效的 PDF
        try:
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF 文件为空"
        except Exception as e:
            return False, f"无效的 PDF 文件: {str(e)}"

        return True, None
