import React, { useState } from 'react';
import { Layout, Input, Button, Card, List, Typography, Space, Tag, message, Row, Col } from 'antd';
import { SearchOutlined, UploadOutlined, StarOutlined, ThunderboltOutlined, FileTextOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../api';
import ScaleIcon from '../components/ScaleIcon';
import EmptyState from '../components/EmptyState';
import theme from '../styles/theme';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Search } = Input;

interface Case {
  id: number;
  case_number: string;
  title: string;
  court: string;
  case_type: string;
  judgment_date: string;
  is_real?: string;
  source?: string;
}

const Home: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const onSearch = async (query: string) => {
    if (!query.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }

    setLoading(true);
    try {
      const response = await casesAPI.search({ query, page: 1, page_size: 20 });
      setCases(response.data.results);
      setTotal(response.data.total);
      message.success(`找到 ${response.data.total} 个相关案例`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: theme.colors.gradient }}>
      <Header style={{
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '0 50px',
        boxShadow: theme.shadows.header,
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
            <div style={{
              width: theme.logo.size,
              height: theme.logo.size,
              borderRadius: theme.logo.borderRadius,
              background: theme.logo.background,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: theme.logo.boxShadow
            }}>
              <ScaleIcon style={{ fontSize: theme.logo.fontSize, color: '#fff' }} />
            </div>
            <Title level={3} style={{
              margin: 0,
              ...theme.title
            }}>
              法律 AI 助手
            </Title>
          </div>
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => navigate('/upload')}
              style={{
                background: theme.colors.gradient,
                border: 'none',
                borderRadius: theme.borderRadius.medium
              }}
            >
              上传文书
            </Button>
            <Button
              icon={<StarOutlined />}
              onClick={() => navigate('/favorites')}
              style={{ borderRadius: theme.borderRadius.medium }}
            >
              我的收藏
            </Button>
            <Button onClick={() => navigate('/login')} style={{ borderRadius: theme.borderRadius.medium }}>退出</Button>
          </Space>
        </div>
      </Header>

      <Content style={{ padding: '60px 50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          {/* Hero Section */}
          {cases.length === 0 && (
            <div style={{ textAlign: 'center', marginBottom: 60 }}>
              <Title level={1} style={{ color: '#fff', fontSize: 48, marginBottom: 16 }}>
                让法律判决书人人都能看懂
              </Title>
              <Paragraph style={{ color: 'rgba(255,255,255,0.9)', fontSize: 18, marginBottom: 40 }}>
                AI 双视角分析 · 专业版 + 普通人版 · 智能解读法律文书
              </Paragraph>

              {/* Feature Cards */}
              <Row gutter={[24, 24]} style={{ marginBottom: 40 }}>
                <Col xs={24} sm={12} md={6}>
                  <Card
                    style={{
                      borderRadius: 16,
                      background: 'rgba(255,255,255,0.95)',
                      border: 'none',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                    }}
                    bodyStyle={{ textAlign: 'center', padding: 24 }}
                  >
                    <ThunderboltOutlined style={{ fontSize: 40, color: '#667eea', marginBottom: 12 }} />
                    <Title level={4}>AI 智能分析</Title>
                    <Text type="secondary">双视角解读判决书</Text>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card
                    style={{
                      borderRadius: 16,
                      background: 'rgba(255,255,255,0.95)',
                      border: 'none',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                    }}
                    bodyStyle={{ textAlign: 'center', padding: 24 }}
                  >
                    <FileTextOutlined style={{ fontSize: 40, color: '#667eea', marginBottom: 12 }} />
                    <Title level={4}>PDF 导入导出</Title>
                    <Text type="secondary">上传文书，导出报告</Text>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card
                    style={{
                      borderRadius: 16,
                      background: 'rgba(255,255,255,0.95)',
                      border: 'none',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                    }}
                    bodyStyle={{ textAlign: 'center', padding: 24 }}
                  >
                    <StarOutlined style={{ fontSize: 40, color: '#667eea', marginBottom: 12 }} />
                    <Title level={4}>收藏笔记</Title>
                    <Text type="secondary">记录个人想法</Text>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={6}>
                  <Card
                    style={{
                      borderRadius: 16,
                      background: 'rgba(255,255,255,0.95)',
                      border: 'none',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                    }}
                    bodyStyle={{ textAlign: 'center', padding: 24 }}
                  >
                    <ScaleIcon style={{ fontSize: 40, color: '#667eea', marginBottom: 12 }} />
                    <Title level={4}>真实案例</Title>
                    <Text type="secondary">最高法公报案例</Text>
                  </Card>
                </Col>
              </Row>
            </div>
          )}

          {/* Search Box */}
          <Card
            style={{
              borderRadius: 16,
              marginBottom: 24,
              background: 'rgba(255,255,255,0.95)',
              border: 'none',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
            }}
          >
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2} style={{ marginBottom: 8 }}>智能案例检索</Title>
                <Paragraph type="secondary">
                  输入关键词，快速查找相关法律案例
                </Paragraph>
              </div>

              <Search
                placeholder="例如：劳动合同纠纷、交通事故赔偿、离婚财产分割..."
                enterButton={
                  <Button
                    type="primary"
                    icon={<SearchOutlined />}
                    style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      border: 'none'
                    }}
                  >
                    搜索
                  </Button>
                }
                size="large"
                onSearch={onSearch}
                loading={loading}
                style={{ borderRadius: 8 }}
              />

              {total > 0 ? (
                <div>
                  <Title level={4}>搜索结果（共 {total} 条）</Title>
                  <List
                    dataSource={cases}
                    renderItem={(item) => (
                      <List.Item
                        key={item.id}
                        style={{
                          background: '#fff',
                          borderRadius: 12,
                          marginBottom: 16,
                          padding: 20,
                          border: '1px solid #f0f0f0',
                          cursor: 'pointer',
                          transition: 'all 0.3s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)';
                          e.currentTarget.style.borderColor = '#667eea';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.boxShadow = 'none';
                          e.currentTarget.style.borderColor = '#f0f0f0';
                        }}
                        onClick={() => navigate(`/case/${item.id}`)}
                        actions={[
                          <Button
                            type="link"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/case/${item.id}`);
                            }}
                            style={{ color: '#667eea' }}
                          >
                            查看详情 →
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <a
                                onClick={(e) => {
                                  e.stopPropagation();
                                  navigate(`/case/${item.id}`);
                                }}
                                style={{ fontSize: 16, fontWeight: 500 }}
                              >
                                {item.title}
                              </a>
                              {item.is_real === 'real' && (
                                <Tag color="green" style={{ borderRadius: 4 }}>真实案例</Tag>
                              )}
                              {item.is_real === 'example' && (
                                <Tag color="orange" style={{ borderRadius: 4 }}>教学示例</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size="small" style={{ marginTop: 8 }}>
                              <Space wrap>
                                <Tag color="blue" style={{ borderRadius: 4 }}>{item.case_type}</Tag>
                                <Tag style={{ borderRadius: 4 }}>{item.court}</Tag>
                                <span style={{ color: '#999' }}>{item.judgment_date}</span>
                              </Space>
                              {item.source && (
                                <span style={{ fontSize: 12, color: '#8c8c8c' }}>
                                  来源：{item.source}
                                </span>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              ) : cases.length === 0 && !loading && (
                <EmptyState
                  type="search"
                  description="输入关键词开始搜索案例"
                />
              )}
            </Space>
          </Card>
        </div>
      </Content>

      <Footer style={{ textAlign: 'center', background: 'transparent', color: 'rgba(255,255,255,0.8)' }}>
        <Space direction="vertical" size="small">
          <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
            法律 AI 助手 © 2026 - 让法律判决书人人都能看懂
          </Text>
          <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 12 }}>
            本系统提供的 AI 分析仅供参考，不构成法律意见
          </Text>
        </Space>
      </Footer>
    </Layout>
  );
};

export default Home;
