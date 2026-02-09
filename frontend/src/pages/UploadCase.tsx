import React, { useState } from 'react';
import { Upload, Button, Card, message, Progress, Space, Typography, Alert, Layout, Row, Col } from 'antd';
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined, RocketOutlined, CloudUploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../api';
import PageHeader from '../components/PageHeader';
import theme from '../styles/theme';

const { Dragger } = Upload;
const { Text, Paragraph, Title } = Typography;
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

  const features = [
    { icon: <FileTextOutlined />, text: '提取 PDF 文本内容' },
    { icon: <CheckCircleOutlined />, text: '识别案号、法院、日期等信息' },
    { icon: <RocketOutlined />, text: '支持后续 AI 智能分析' },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: theme.colors.background.secondary }}>
      <PageHeader title="上传法律文书" showBackButton />

      <Content style={{ padding: '40px' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          {/* 标题区域 */}
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <div style={{
              width: 72,
              height: 72,
              borderRadius: 18,
              background: theme.colors.gradientHero,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
              boxShadow: theme.shadows.lg,
            }}>
              <CloudUploadOutlined style={{ fontSize: 36, color: '#fff' }} />
            </div>
            <Title level={2} style={{ marginBottom: 12, color: theme.colors.text.primary }}>
              上传法律文书
            </Title>
            <Text type="secondary" style={{ fontSize: 16 }}>
              上传您的法律判决书 PDF 文件，系统将自动提取内容并进行智能分析
            </Text>
          </div>

          <Row gutter={24}>
            {/* 上传区域 */}
            <Col xs={24} lg={14}>
              <Card
                style={{
                  borderRadius: theme.borderRadius['2xl'],
                  border: `1px solid ${theme.colors.border.light}`,
                  boxShadow: theme.shadows.card,
                  marginBottom: 24,
                }}
                styles={{ body: { padding: 32 } }}
              >
                <Dragger
                  {...uploadProps}
                  disabled={uploading}
                  style={{
                    background: theme.colors.background.tertiary,
                    border: `2px dashed ${theme.colors.border.medium}`,
                    borderRadius: theme.borderRadius.xlarge,
                    padding: '40px 20px',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <p className="ant-upload-drag-icon" style={{ marginBottom: 20 }}>
                    <InboxOutlined style={{ fontSize: 56, color: theme.colors.primary }} />
                  </p>
                  <p style={{
                    fontSize: 18,
                    fontWeight: 500,
                    color: theme.colors.text.primary,
                    marginBottom: 12,
                  }}>
                    点击或拖拽文件到此区域上传
                  </p>
                  <p style={{ color: theme.colors.text.tertiary, fontSize: 14 }}>
                    支持 PDF 格式，文件大小不超过 10MB
                  </p>
                </Dragger>

                {uploading && (
                  <div style={{ marginTop: 24 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      marginBottom: 12,
                    }}>
                      <CloudUploadOutlined style={{ color: theme.colors.primary, fontSize: 20 }} />
                      <Text style={{ fontSize: 15 }}>正在上传和处理文件...</Text>
                    </div>
                    <Progress
                      percent={uploadProgress}
                      status="active"
                      strokeColor={{
                        '0%': theme.colors.primary,
                        '100%': theme.colors.primaryLight,
                      }}
                      trailColor={theme.colors.background.tertiary}
                    />
                  </div>
                )}
              </Card>
            </Col>

            {/* 说明区域 */}
            <Col xs={24} lg={10}>
              <Space direction="vertical" size={20} style={{ width: '100%' }}>
                <Alert
                  message={<Text strong>支持的文件格式</Text>}
                  description={
                    <ul style={{ marginBottom: 0, paddingLeft: 20, marginTop: 8 }}>
                      <li style={{ marginBottom: 6 }}>PDF 格式（推荐）</li>
                      <li style={{ marginBottom: 6 }}>文件大小不超过 10MB</li>
                      <li>支持扫描件和电子文档</li>
                    </ul>
                  }
                  type="info"
                  showIcon
                  style={{
                    borderRadius: theme.borderRadius.large,
                    border: 'none',
                  }}
                />

                <Card
                  size="small"
                  title={
                    <Space>
                      <RocketOutlined style={{ color: theme.colors.success }} />
                      <Text strong>上传后系统将自动</Text>
                    </Space>
                  }
                  style={{
                    borderRadius: theme.borderRadius.large,
                    border: `1px solid ${theme.colors.border.light}`,
                  }}
                >
                  <Space direction="vertical" size={12} style={{ width: '100%' }}>
                    {features.map((feature, index) => (
                      <div
                        key={index}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 12,
                          padding: '10px 14px',
                          background: theme.colors.background.tertiary,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      >
                        <span style={{ color: theme.colors.success, fontSize: 18 }}>
                          {feature.icon}
                        </span>
                        <Text style={{ fontSize: 14 }}>{feature.text}</Text>
                      </div>
                    ))}
                  </Space>
                </Card>

                <Alert
                  message={<Text strong>温馨提示</Text>}
                  description="上传的文件将保存到您的案例库中，您可以随时进行 AI 智能分析和导出报告。"
                  type="success"
                  showIcon
                  style={{
                    borderRadius: theme.borderRadius.large,
                    border: 'none',
                  }}
                />
              </Space>
            </Col>
          </Row>
        </div>
      </Content>
    </Layout>
  );
};

export default UploadCase;
