import React, { useEffect, useState } from 'react';
import { Layout, Card, List, Button, Typography, Space, Tag, message, Row, Col } from 'antd';
import { useNavigate } from 'react-router-dom';
import { StarFilled, DeleteOutlined, EyeOutlined, CalendarOutlined, BankOutlined } from '@ant-design/icons';
import { favoritesAPI, casesAPI } from '../api';
import PageHeader from '../components/PageHeader';
import Loading from '../components/Loading';
import EmptyState from '../components/EmptyState';
import theme from '../styles/theme';

const { Content } = Layout;
const { Title, Text } = Typography;

interface Favorite {
  id: number;
  case_id: number;
  created_at: string;
}

interface CaseInfo {
  id: number;
  case_number: string;
  title: string;
  court: string;
  case_type: string;
  judgment_date: string;
}

const MyFavorites: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [casesMap, setCasesMap] = useState<Map<number, CaseInfo>>(new Map());

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const response = await favoritesAPI.getFavorites();
      const favs = response.data;
      setFavorites(favs);

      // 获取每个收藏案例的详细信息
      const casesData = new Map<number, CaseInfo>();
      for (const fav of favs) {
        try {
          const caseResponse = await casesAPI.getCase(fav.case_id);
          casesData.set(fav.case_id, caseResponse.data);
        } catch (error) {
          console.error(`获取案例 ${fav.case_id} 失败:`, error);
        }
      }
      setCasesMap(casesData);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取收藏列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (caseId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await favoritesAPI.removeFavorite(caseId);
      message.success('已取消收藏');
      fetchFavorites();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh', background: theme.colors.background.secondary }}>
        <PageHeader title="我的收藏" showBackButton />
        <Content style={{ padding: '40px' }}>
          <Loading tip="加载收藏列表..." />
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh', background: theme.colors.background.secondary }}>
      <PageHeader title="我的收藏" showBackButton />

      <Content style={{ padding: '40px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          {/* 标题区域 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 32,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: `${theme.colors.accent}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <StarFilled style={{ fontSize: 24, color: theme.colors.accent }} />
              </div>
              <div>
                <Title level={3} style={{ margin: 0, color: theme.colors.text.primary }}>
                  我的收藏
                </Title>
                <Text type="secondary">共 {favorites.length} 个案例</Text>
              </div>
            </div>
          </div>

          {favorites.length === 0 ? (
            <EmptyState
              type="data"
              description="还没有收藏任何案例"
              action={{
                text: '去搜索案例',
                onClick: () => navigate('/'),
              }}
            />
          ) : (
            <Row gutter={[20, 20]}>
              {favorites.map((item) => {
                const caseInfo = casesMap.get(item.case_id);
                if (!caseInfo) return null;

                return (
                  <Col xs={24} md={12} xl={8} key={item.id}>
                    <Card
                      hoverable
                      onClick={() => navigate(`/case/${item.case_id}`)}
                      style={{
                        borderRadius: theme.borderRadius.xlarge,
                        border: `1px solid ${theme.colors.border.light}`,
                        boxShadow: theme.shadows.card,
                        height: '100%',
                        transition: 'all 0.3s ease',
                      }}
                      styles={{ body: { padding: 24 } }}
                    >
                      <Space direction="vertical" size={16} style={{ width: '100%' }}>
                        {/* 标题和收藏按钮 */}
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          gap: 12,
                        }}>
                          <Title
                            level={5}
                            style={{
                              margin: 0,
                              color: theme.colors.text.primary,
                              flex: 1,
                              lineHeight: 1.4,
                            }}
                            ellipsis={{ rows: 2 }}
                          >
                            {caseInfo.title}
                          </Title>
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={(e) => handleRemoveFavorite(item.case_id, e)}
                            style={{ flexShrink: 0 }}
                          />
                        </div>

                        {/* 案件类型标签 */}
                        <Tag
                          color="blue"
                          style={{
                            borderRadius: theme.borderRadius.small,
                            padding: '2px 10px',
                          }}
                        >
                          {caseInfo.case_type}
                        </Tag>

                        {/* 案件信息 */}
                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: 8,
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <BankOutlined style={{ color: theme.colors.text.tertiary, fontSize: 14 }} />
                            <Text type="secondary" style={{ fontSize: 13 }}>
                              {caseInfo.court}
                            </Text>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <CalendarOutlined style={{ color: theme.colors.text.tertiary, fontSize: 14 }} />
                            <Text type="secondary" style={{ fontSize: 13 }}>
                              {caseInfo.judgment_date}
                            </Text>
                          </div>
                        </div>

                        {/* 底部 */}
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          paddingTop: 12,
                          borderTop: `1px solid ${theme.colors.border.light}`,
                        }}>
                          <Text style={{ fontSize: 12, color: theme.colors.text.tertiary }}>
                            <StarFilled style={{ color: theme.colors.accent, marginRight: 4 }} />
                            收藏于 {new Date(item.created_at).toLocaleDateString('zh-CN')}
                          </Text>
                          <Button
                            type="link"
                            icon={<EyeOutlined />}
                            style={{ color: theme.colors.primary, padding: 0, height: 'auto' }}
                          >
                            查看
                          </Button>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                );
              })}
            </Row>
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default MyFavorites;
