import React, { useState } from 'react';
import { Layout, Input, Button, Card, List, Typography, Space, Tag, message, Row, Col } from 'antd';
import { SearchOutlined, UploadOutlined, StarOutlined, ThunderboltOutlined, FileTextOutlined, SafetyCertificateOutlined, BookOutlined } from '@ant-design/icons';
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

  const features = [
    {
      icon: <ThunderboltOutlined />,
      title: 'AI 智能分析',
      desc: '双视角解读判决书',
      color: theme.colors.primary
    },
    {
      icon: <FileTextOutlined />,
      title: 'PDF 导入导出',
      desc: '上传文书，导出报告',
      color: theme.colors.info
    },
    {
      icon: <BookOutlined />,
      title: '法条知识库',
      desc: 'RAG 增强法律检索',
      color: theme.colors.success
    },
    {
      icon: <SafetyCertificateOutlined />,
      title: '引用溯源',
      desc: '每条分析可追溯验证',
      color: theme.colors.accent
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: theme.colors.background.secondary }}>
      {/* 顶部导航 */}
      <Header style={{
        background: 'rgba(255, 255, 255, 0.98)',
        padding: '0 40px',
        boxShadow: theme.shadows.header,
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: 64,
        lineHeight: '64px',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: 1400,
          margin: '0 auto',
          height: '100%'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
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
            <Title level={4} style={{
              margin: 0,
              ...theme.title,
              fontSize: 20,
            }}>
              法律 AI 助手
            </Title>
          </div>
          <Space size={12}>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => navigate('/upload')}
              style={{
                borderRadius: theme.borderRadius.medium,
                height: 40,
                paddingLeft: 20,
                paddingRight: 20,
              }}
            >
              上传文书
            </Button>
            <Button
              icon={<StarOutlined />}
              onClick={() => navigate('/favorites')}
              style={{
                borderRadius: theme.borderRadius.medium,
                height: 40,
                border: `1px solid ${theme.colors.border.light}`,
              }}
            >
              我的收藏
            </Button>
            <Button
              onClick={() => navigate('/login')}
              style={{
                borderRadius: theme.borderRadius.medium,
                height: 40,
                color: theme.colors.text.secondary,
              }}
            >
              退出
            </Button>
          </Space>
        </div>
      </Header>

      <Content>
        {/* Hero 区域 */}
        {cases.length === 0 && (
          <div style={{
            background: theme.colors.gradientHero,
            padding: '80px 40px 100px',
            position: 'relative',
            overflow: 'hidden',
          }}>
            {/* 背景装饰 */}
            <div style={{
              position: 'absolute',
              top: -100,
              right: -100,
              width: 400,
              height: 400,
              borderRadius: '50%',
              background: 'rgba(212, 168, 75, 0.1)',
              filter: 'blur(60px)',
            }} />
            <div style={{
              position: 'absolute',
              bottom: -50,
              left: -50,
              width: 300,
              height: 300,
              borderRadius: '50%',
              background: 'rgba(45, 90, 138, 0.2)',
              filter: 'blur(40px)',
            }} />

            <div style={{ maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 1 }}>
              <div style={{ textAlign: 'center', marginBottom: 60 }}>
                <Title level={1} style={{
                  color: '#fff',
                  fontSize: 52,
                  marginBottom: 20,
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                }}>
                  让法律判决书
                  <span style={{
                    background: theme.colors.gradientAccent,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    marginLeft: 8,
                  }}>人人都能看懂</span>
                </Title>
                <Paragraph style={{
                  color: 'rgba(255,255,255,0.8)',
                  fontSize: 18,
                  marginBottom: 0,
                  maxWidth: 600,
                  margin: '0 auto',
                  lineHeight: 1.8,
                }}>
                  AI 双视角分析 · 专业版 + 普通人版 · RAG 增强知识检索 · 引用可溯源
                </Paragraph>
              </div>

              {/* 功能卡片 */}
              <Row gutter={[20, 20]}>
                {features.map((feature, index) => (
                  <Col xs={24} sm={12} md={6} key={index}>
                    <Card
                      style={{
                        borderRadius: theme.borderRadius.xlarge,
                        background: 'rgba(255,255,255,0.95)',
                        border: 'none',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
                        cursor: 'default',
                        transition: 'all 0.3s ease',
                      }}
                      styles={{ body: { padding: 28, textAlign: 'center' } }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-4px)';
                        e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.15)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.12)';
                      }}
                    >
                      <div style={{
                        width: 56,
                        height: 56,
                        borderRadius: 14,
                        background: `${feature.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px',
                        fontSize: 26,
                        color: feature.color,
                      }}>
                        {feature.icon}
                      </div>
                      <Title level={5} style={{ marginBottom: 8, fontWeight: 600 }}>
                        {feature.title}
                      </Title>
                      <Text type="secondary" style={{ fontSize: 14 }}>
                        {feature.desc}
                      </Text>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          </div>
        )}

        {/* 搜索区域 */}
        <div style={{
          padding: cases.length === 0 ? '0 40px 60px' : '40px',
          marginTop: cases.length === 0 ? -50 : 0,
          position: 'relative',
          zIndex: 2,
        }}>
          <div style={{ maxWidth: 1200, margin: '0 auto' }}>
            <Card
              style={{
                borderRadius: theme.borderRadius['2xl'],
                background: '#fff',
                border: `1px solid ${theme.colors.border.light}`,
                boxShadow: cases.length === 0
                  ? '0 20px 60px rgba(0,0,0,0.1)'
                  : theme.shadows.card,
              }}
              styles={{ body: { padding: cases.length === 0 ? 48 : 32 } }}
            >
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                {cases.length === 0 && (
                  <div style={{ textAlign: 'center', marginBottom: 8 }}>
                    <Title level={3} style={{ marginBottom: 8, fontWeight: 600 }}>
                      智能案例检索
                    </Title>
                    <Text type="secondary" style={{ fontSize: 15 }}>
                      输入关键词，快速查找相关法律案例，支持语义搜索
                    </Text>
                  </div>
                )}

                <Search
                  placeholder="例如：劳动合同纠纷、交通事故赔偿、离婚财产分割、消费者维权..."
                  enterButton={
                    <Button
                      type="primary"
                      icon={<SearchOutlined />}
                      style={{ height: 52, paddingLeft: 28, paddingRight: 28 }}
                    >
                      搜索案例
                    </Button>
                  }
                  size="large"
                  onSearch={onSearch}
                  loading={loading}
                  style={{ maxWidth: 800, margin: '0 auto', display: 'block' }}
                />

                {total > 0 && (
                  <div style={{ marginTop: 24 }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: 20,
                    }}>
                      <Title level={4} style={{ margin: 0 }}>
                        搜索结果
                      </Title>
                      <Tag style={{
                        background: theme.colors.primary,
                        color: '#fff',
                        border: 'none',
                        padding: '4px 12px',
                        fontSize: 13,
                      }}>
                        共 {total} 条
                      </Tag>
                    </div>

                    <List
                      dataSource={cases}
                      renderItem={(item) => (
                        <div
                          key={item.id}
                          onClick={() => navigate(`/case/${item.id}`)}
                          style={{
                            background: '#fff',
                            borderRadius: theme.borderRadius.large,
                            marginBottom: 12,
                            padding: 24,
                            border: `1px solid ${theme.colors.border.light}`,
                            cursor: 'pointer',
                            transition: 'all 0.25s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.boxShadow = theme.shadows.cardHover;
                            e.currentTarget.style.borderColor = theme.colors.primary;
                            e.currentTarget.style.transform = 'translateX(4px)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.boxShadow = 'none';
                            e.currentTarget.style.borderColor = theme.colors.border.light;
                            e.currentTarget.style.transform = 'translateX(0)';
                          }}
                        >
                          <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                          }}>
                            <div style={{ flex: 1 }}>
                              <div style={{ marginBottom: 12 }}>
                                <Text strong style={{
                                  fontSize: 17,
                                  color: theme.colors.text.primary,
                                  marginRight: 12,
                                }}>
                                  {item.title}
                                </Text>
                                {item.is_real === 'real' && (
                                  <Tag color="green" style={{ borderRadius: 4 }}>真实案例</Tag>
                                )}
                                {item.is_real === 'example' && (
                                  <Tag color="orange" style={{ borderRadius: 4 }}>教学示例</Tag>
                                )}
                                {item.is_real === 'upload' && (
                                  <Tag color="blue" style={{ borderRadius: 4 }}>用户上传</Tag>
                                )}
                              </div>
                              <Space wrap size={8}>
                                <Tag style={{
                                  background: `${theme.colors.primary}10`,
                                  color: theme.colors.primary,
                                  border: 'none',
                                }}>
                                  {item.case_type}
                                </Tag>
                                <Text type="secondary" style={{ fontSize: 13 }}>
                                  {item.court}
                                </Text>
                                <Text type="secondary" style={{ fontSize: 13 }}>
                                  {item.judgment_date}
                                </Text>
                              </Space>
                              {item.source && (
                                <div style={{ marginTop: 8 }}>
                                  <Text style={{ fontSize: 12, color: theme.colors.text.tertiary }}>
                                    来源：{item.source}
                                  </Text>
                                </div>
                              )}
                            </div>
                            <Button
                              type="link"
                              style={{
                                color: theme.colors.primary,
                                fontWeight: 500,
                                paddingRight: 0,
                              }}
                            >
                              查看详情 →
                            </Button>
                          </div>
                        </div>
                      )}
                    />
                  </div>
                )}

                {cases.length === 0 && !loading && total === 0 && (
                  <EmptyState
                    type="search"
                    description="输入关键词开始搜索案例"
                  />
                )}
              </Space>
            </Card>
          </div>
        </div>
      </Content>

      <Footer style={{
        textAlign: 'center',
        background: theme.colors.background.secondary,
        padding: '32px 40px',
        borderTop: `1px solid ${theme.colors.border.light}`,
      }}>
        <Space direction="vertical" size={8}>
          <Text style={{ color: theme.colors.text.secondary, fontSize: 14 }}>
            法律 AI 助手 © 2026 - 让法律判决书人人都能看懂
          </Text>
          <Text style={{ color: theme.colors.text.tertiary, fontSize: 12 }}>
            本系统提供的 AI 分析仅供参考，不构成法律意见
          </Text>
        </Space>
      </Footer>
    </Layout>
  );
};

export default Home;
