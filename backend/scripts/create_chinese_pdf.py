"""使用 PyPDF2 创建简单的测试 PDF"""
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from io import BytesIO

# 注册中文字体
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 创建 PDF
buffer = BytesIO()
c = canvas.Canvas(buffer, pagesize=A4)
width, height = A4

# 设置中文字体
c.setFont('STSong-Light', 12)

# 测试内容
content = """北京市第一中级人民法院
民事判决书

(2023)京01民终1234号

原告：张三
被告：某科技有限公司

本院认为，原告张三与被告某科技有限公司因劳动合同纠纷一案，
原告请求被告支付未签订书面劳动合同的双倍工资差额。

经审理查明：
1. 原告于2022年1月1日入职被告公司
2. 双方未签订书面劳动合同
3. 原告月工资为8000元

根据《中华人民共和国劳动合同法》第八十二条规定：
用人单位自用工之日起超过一个月不满一年未与劳动者订立书面劳动合同的，
应当向劳动者每月支付二倍的工资。

判决如下：
一、被告某科技有限公司于本判决生效之日起十日内支付原告张三
    未签订书面劳动合同的双倍工资差额88000元。
二、驳回原告张三的其他诉讼请求。

审判长：李四
审判员：王五
书记员：赵六

二〇二三年六月十五日"""

# 写入内容
y = height - 50
for line in content.split('\n'):
    if y < 50:
        c.showPage()
        c.setFont('STSong-Light', 12)
        y = height - 50
    c.drawString(50, y, line)
    y -= 20

c.save()

# 保存到文件
buffer.seek(0)
with open('/tmp/test_case_chinese.pdf', 'wb') as f:
    f.write(buffer.read())

print("中文 PDF 已创建: /tmp/test_case_chinese.pdf")
