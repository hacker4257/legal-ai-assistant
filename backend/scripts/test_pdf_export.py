"""测试 PDF 导出功能"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_export_service import PDFExportService


async def test_pdf_export():
    """测试 PDF 导出"""

    # 模拟案例信息
    case_info = {
        "title": "张三诉某公司劳动合同纠纷案",
        "case_number": "(2023)京01民终1234号",
        "court": "北京市第一中级人民法院",
        "case_type": "民事",
        "judgment_date": "2023-06-15",
    }

    # 模拟分析结果
    analysis = {
        "summary": "这是案情摘要",
        "summary_plain": "这是通俗版案情摘要",
        "key_elements": {
            "parties": "原告张三，被告某公司",
            "case_cause": "劳动合同纠纷",
        },
        "key_elements_plain": {
            "who": "张三和某公司",
            "what_happened": "劳动合同纠纷",
        },
        "legal_reasoning": "法院认为...",
        "legal_reasoning_plain": "法院觉得...",
        "legal_basis": ["劳动合同法第39条", "劳动合同法第82条"],
        "legal_basis_plain": ["劳动合同法第39条：...", "劳动合同法第82条：..."],
        "judgment_result": "判决如下...",
        "judgment_result_plain": "判决结果是...",
        "plain_language_tips": "给你的建议：..."
    }

    print("=" * 60)
    print("测试 PDF 导出功能")
    print("=" * 60)

    try:
        # 测试双视角导出
        print("\n1. 测试双视角导出...")
        pdf_bytes = PDFExportService.generate_analysis_pdf(
            case_info=case_info,
            analysis=analysis,
            perspective="both"
        )
        print(f"✓ 双视角 PDF 生成成功，大小: {len(pdf_bytes)} 字节")

        # 保存到文件
        output_path = Path("/tmp/test_both.pdf")
        output_path.write_bytes(pdf_bytes)
        print(f"✓ 已保存到: {output_path}")

        # 测试普通人版导出
        print("\n2. 测试普通人版导出...")
        pdf_bytes = PDFExportService.generate_analysis_pdf(
            case_info=case_info,
            analysis=analysis,
            perspective="plain"
        )
        print(f"✓ 普通人版 PDF 生成成功，大小: {len(pdf_bytes)} 字节")

        # 测试专业版导出
        print("\n3. 测试专业版导出...")
        pdf_bytes = PDFExportService.generate_analysis_pdf(
            case_info=case_info,
            analysis=analysis,
            perspective="professional"
        )
        print(f"✓ 专业版 PDF 生成成功，大小: {len(pdf_bytes)} 字节")

        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pdf_export())
