import React, { useState } from 'react';
import { Upload, Button, Card, message, Progress, Space, Typography, Alert, Layout } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../api';
import PageHeader from '../components/PageHeader';

const { Dragger } = Upload;
const { Text, Paragraph } = Typography;
const { Content } = Layout;

const UploadCase: React.FC = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await casesAPI.uploadPDF(file, (progressEvent: any) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percent);
      });

      message.success('上传成功！正在跳转到案例详情...');

      // 跳转到案例详情页
      setTimeout(() => {
        navigate(`/case/${response.data.id}`);
      }, 1000);
    } catch (error: any) {
      console.error('上传失败:', error);
      message.error(error.response?.data?.detail || '上传失败，请重试');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf',
    beforeUpload: (file: File) => {
      const isPDF = file.type === 'application/pdf';
      if (!isPDF) {
        message.error('只能上传 PDF 格式的文件！');
        return false;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB！');
        return false;
      }

      handleUpload(file);
      return false; // 阻止自动上传
    },
    showUploadList: false,
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <PageHeader title="上传法律文书" showBackButton />

      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Paragraph type="secondary">
                  上传您的法律判决书 PDF 文件，系统将自动提取内容并进行智能分析
                </Paragraph>
              </div>

              <Alert
                message="支持的文件格式"
                description={
                  <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                    <li>PDF 格式（推荐）</li>
                    <li>文件大小不超过 10MB</li>
                    <li>支持扫描件和电子文档</li>
                  </ul>
                }
                type="info"
                showIcon
              />

              <Dragger {...uploadProps} disabled={uploading}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持 PDF 格式，文件大小不超过 10MB
                </p>
              </Dragger>

              {uploading && (
                <div>
                  <Text>正在上传和处理文件...</Text>
                  <Progress percent={uploadProgress} status="active" />
                </div>
              )}

              <Alert
                message="功能说明"
                description={
                  <div>
                    <p><strong>上传后系统将自动：</strong></p>
                    <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                      <li>提取 PDF 文本内容</li>
                      <li>识别案号、法院、日期等信息</li>
                      <li>提取当事人信息</li>
                      <li>保存到您的案例库</li>
                      <li>支持后续 AI 智能分析</li>
                    </ul>
                  </div>
                }
                type="success"
                showIcon
              />
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default UploadCase;
