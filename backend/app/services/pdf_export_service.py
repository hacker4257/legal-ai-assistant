"""PDF 导出服务"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from io import BytesIO


class PDFExportService:
    """PDF 导出服务"""

    @staticmethod
    def generate_analysis_pdf(
        case_info: Dict[str, Any],
        analysis: Dict[str, Any],
        perspective: str = "both"  # both, professional, plain
    ) -> bytes:
        """
        生成分析报告 PDF

        Args:
            case_info: 案例信息
            analysis: 分析结果
            perspective: 视角 (both/professional/plain)

        Returns:
            PDF 字节流
        """
        # 延迟导入，避免启动时缺少系统库导致失败
        try:
            import markdown
            from weasyprint import HTML, CSS
        except ImportError as e:
            raise ImportError(f"PDF 导出需要安装 weasyprint 及其系统依赖: {e}")

        # 生成 HTML
        html_content = PDFExportService._generate_html(case_info, analysis, perspective)

        # 转换为 PDF
        pdf_bytes = HTML(string=html_content).write_pdf(
            stylesheets=[CSS(string=PDFExportService._get_css())]
        )

        return pdf_bytes

    @staticmethod
    def _generate_html(
        case_info: Dict[str, Any],
        analysis: Dict[str, Any],
        perspective: str
    ) -> str:
        """生成 HTML 内容"""
        import markdown

        # 转换 Markdown 到 HTML（使用简单配置）
        md = markdown.Markdown()

        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>案例分析报告</title>',
            '</head>',
            '<body>',
            '<div class="container">',
        ]

        # 标题页
        html_parts.extend([
            '<div class="title-page">',
            '<h1>法律案例智能分析报告</h1>',
            f'<h2>{case_info.get("title", "")}</h2>',
            '<div class="meta">',
            f'<p><strong>案号：</strong>{case_info.get("case_number", "")}</p>',
            f'<p><strong>法院：</strong>{case_info.get("court", "")}</p>',
            f'<p><strong>案件类型：</strong>{case_info.get("case_type", "")}</p>',
            f'<p><strong>判决日期：</strong>{case_info.get("judgment_date", "")}</p>',
            f'<p><strong>生成时间：</strong>{datetime.now().strftime("%Y年%m月%d日 %H:%M")}</p>',
            '</div>',
            '</div>',
        ])

        # 根据视角生成内容
        if perspective in ["both", "plain"]:
            html_parts.extend([
                '<div class="section">',
                '<h2 class="section-title plain">📖 普通人视角</h2>',
                '<div class="perspective-badge plain">用大白话解释</div>',
            ])

            # 案情摘要
            if analysis.get("summary_plain"):
                html_parts.extend([
                    '<h3>案情摘要</h3>',
                    '<div class="content">',
                    md.convert(analysis["summary_plain"]),
                    '</div>',
                ])

            # 关键要素
            if analysis.get("key_elements_plain"):
                html_parts.extend([
                    '<h3>关键要素</h3>',
                    '<div class="content">',
                ])
                key_elements = analysis["key_elements_plain"]
                if isinstance(key_elements, dict):
                    # 如果是字典，转换为中文标签
                    key_mapping = {
                        "who": "当事人",
                        "what_happened": "发生了什么",
                        "what_they_want": "诉求",
                        "parties": "当事人",
                        "case_cause": "案由",
                        "dispute_focus": "争议焦点"
                    }
                    for key, value in key_elements.items():
                        label = key_mapping.get(key, key)
                        html_parts.append(f'<p><strong>{label}：</strong>{value}</p>')
                else:
                    # 如果是字符串，直接转换
                    html_parts.append(md.convert(str(key_elements)))
                html_parts.append('</div>')

            # 判决理由
            if analysis.get("legal_reasoning_plain"):
                html_parts.extend([
                    '<h3>判决理由</h3>',
                    '<div class="content">',
                    md.convert(analysis["legal_reasoning_plain"]),
                    '</div>',
                ])

            # 法律依据
            if analysis.get("legal_basis_plain"):
                html_parts.extend([
                    '<h3>法律依据</h3>',
                    '<div class="content">',
                ])
                legal_basis = analysis["legal_basis_plain"]
                if isinstance(legal_basis, list):
                    # 如果是列表，转换为 HTML 列表
                    html_parts.append('<ul>')
                    for item in legal_basis:
                        html_parts.append(f'<li>{item}</li>')
                    html_parts.append('</ul>')
                else:
                    # 如果是字符串，直接转换
                    html_parts.append(md.convert(str(legal_basis)))
                html_parts.append('</div>')

            # 裁判结果
            if analysis.get("judgment_result_plain"):
                html_parts.extend([
                    '<h3>裁判结果</h3>',
                    '<div class="content">',
                    md.convert(analysis["judgment_result_plain"]),
                    '</div>',
                ])

            # 给你的建议
            if analysis.get("plain_language_tips"):
                html_parts.extend([
                    '<h3>💡 给你的建议</h3>',
                    '<div class="content tips">',
                    md.convert(analysis["plain_language_tips"]),
                    '</div>',
                ])

            html_parts.append('</div>')

        if perspective in ["both", "professional"]:
            html_parts.extend([
                '<div class="section">',
                '<h2 class="section-title professional">👔 专业视角</h2>',
                '<div class="perspective-badge professional">法律专业术语</div>',
            ])

            # 案情摘要
            if analysis.get("summary"):
                html_parts.extend([
                    '<h3>案情摘要</h3>',
                    '<div class="content">',
                    md.convert(analysis["summary"]),
                    '</div>',
                ])

            # 关键要素
            if analysis.get("key_elements"):
                html_parts.extend([
                    '<h3>关键要素</h3>',
                    '<div class="content">',
                ])
                key_elements = analysis["key_elements"]
                if isinstance(key_elements, dict):
                    # 如果是字典，转换为中文标签
                    key_mapping = {
                        "parties": "当事人",
                        "case_cause": "案由",
                        "dispute_focus": "争议焦点",
                        "who": "当事人",
                        "what_happened": "发生了什么",
                        "what_they_want": "诉求"
                    }
                    for key, value in key_elements.items():
                        label = key_mapping.get(key, key)
                        html_parts.append(f'<p><strong>{label}：</strong>{value}</p>')
                else:
                    # 如果是字符串，直接转换
                    html_parts.append(md.convert(str(key_elements)))
                html_parts.append('</div>')

            # 判决理由
            if analysis.get("legal_reasoning"):
                html_parts.extend([
                    '<h3>判决理由</h3>',
                    '<div class="content">',
                    md.convert(analysis["legal_reasoning"]),
                    '</div>',
                ])

            # 法律依据
            if analysis.get("legal_basis"):
                html_parts.extend([
                    '<h3>法律依据</h3>',
                    '<div class="content">',
                    '<ul>',
                ])
                for basis in analysis["legal_basis"]:
                    html_parts.append(f'<li>{basis}</li>')
                html_parts.extend([
                    '</ul>',
                    '</div>',
                ])

            # 裁判结果
            if analysis.get("judgment_result"):
                html_parts.extend([
                    '<h3>裁判结果</h3>',
                    '<div class="content">',
                    md.convert(analysis["judgment_result"]),
                    '</div>',
                ])

            html_parts.append('</div>')

        # 页脚
        html_parts.extend([
            '<div class="footer">',
            '<p>本报告由法律 AI 助手自动生成，仅供参考，不构成法律意见。</p>',
            '<p>如需专业法律建议，请咨询执业律师。</p>',
            '</div>',
            '</div>',
            '</body>',
            '</html>',
        ])

        return '\n'.join(html_parts)

    @staticmethod
    def _get_css() -> str:
        """获取 CSS 样式"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: counter(page) " / " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }

        body {
            font-family: "Noto Sans CJK SC", "Source Han Sans CN", "Microsoft YaHei", "SimSun", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }

        .container {
            max-width: 100%;
        }

        .title-page {
            text-align: center;
            padding: 60px 0;
            border-bottom: 3px solid #1890ff;
            margin-bottom: 40px;
        }

        .title-page h1 {
            font-size: 28pt;
            color: #1890ff;
            margin-bottom: 20px;
        }

        .title-page h2 {
            font-size: 18pt;
            color: #333;
            margin-bottom: 30px;
        }

        .meta {
            text-align: left;
            display: inline-block;
            margin-top: 30px;
        }

        .meta p {
            margin: 8px 0;
            font-size: 11pt;
        }

        .section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }

        .section-title {
            font-size: 18pt;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ddd;
        }

        .section-title.plain {
            color: #52c41a;
        }

        .section-title.professional {
            color: #1890ff;
        }

        .perspective-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 10pt;
            margin-bottom: 20px;
        }

        .perspective-badge.plain {
            background: #f6ffed;
            color: #52c41a;
            border: 1px solid #b7eb8f;
        }

        .perspective-badge.professional {
            background: #e6f7ff;
            color: #1890ff;
            border: 1px solid #91d5ff;
        }

        h3 {
            font-size: 14pt;
            color: #333;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .content {
            margin-bottom: 20px;
            padding: 15px;
            background: #fafafa;
            border-left: 3px solid #1890ff;
        }

        .content.tips {
            background: #fffbe6;
            border-left-color: #faad14;
        }

        .content p {
            margin: 10px 0;
        }

        .content ul, .content ol {
            margin: 10px 0;
            padding-left: 25px;
        }

        .content li {
            margin: 5px 0;
        }

        .content strong {
            color: #1890ff;
        }

        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 9pt;
            color: #999;
        }

        .footer p {
            margin: 5px 0;
        }
        """
