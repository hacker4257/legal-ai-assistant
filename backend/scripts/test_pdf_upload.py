"""测试 PDF 上传功能"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_service import PDFService


async def test_pdf_upload():
    """测试 PDF 处理"""
    pdf_path = "/tmp/test_case_chinese.pdf"

    print("=" * 60)
    print("测试 PDF 上传功能")
    print("=" * 60)

    # 1. 验证 PDF
    print("\n1. 验证 PDF 文件...")
    is_valid, error_msg = PDFService.validate_pdf(pdf_path)
    if is_valid:
        print("✓ PDF 文件有效")
    else:
        print(f"✗ PDF 文件无效: {error_msg}")
        return

    # 2. 提取文本
    print("\n2. 提取文本内容...")
    text = PDFService.extract_text(pdf_path)
    print(f"✓ 提取文本长度: {len(text)} 字符")
    print(f"\n文本预览:\n{text[:500]}...")

    # 3. 解析案件信息
    print("\n3. 解析案件信息...")
    case_info = PDFService.parse_case_info(text)
    print(f"✓ 案号: {case_info['case_number']}")
    print(f"✓ 标题: {case_info['title']}")
    print(f"✓ 法院: {case_info['court']}")
    print(f"✓ 案件类型: {case_info['case_type']}")
    print(f"✓ 判决日期: {case_info['judgment_date']}")
    print(f"✓ 当事人: {case_info['parties']}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_pdf_upload())
