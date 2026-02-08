import React, { useEffect, useState } from 'react';
import { Layout, Card, List, Button, Typography, Space, Tag, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { favoritesAPI, casesAPI } from '../api';
import PageHeader from '../components/PageHeader';
import Loading from '../components/Loading';
import EmptyState from '../components/EmptyState';

const { Content } = Layout;
const { Title } = Typography;

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

  const handleRemoveFavorite = async (caseId: number) => {
    try {
      await favoritesAPI.removeFavorite(caseId);
      message.success('已取消收藏');
      fetchFavorites();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 50px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
            }}>
              <ScaleIcon style={{ fontSize: 24, color: '#fff' }} />
            </div>
            <Title level={3} style={{
              margin: 0,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 600
            }}>
              我的收藏
            </Title>
          </div>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>
            返回首页
          </Button>
        </div>
      </Header>

      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Card>
            {favorites.length === 0 && !loading ? (
              <Empty description="还没有收藏任何案例" />
            ) : (
              <List
                loading={loading}
                dataSource={favorites}
                renderItem={(item) => {
                  const caseInfo = casesMap.get(item.case_id);
                  if (!caseInfo) return null;

                  return (
                    <List.Item
                      actions={[
                        <Button
                          type="link"
                          onClick={() => navigate(`/case/${item.case_id}`)}
                        >
                          查看详情
                        </Button>,
                        <Button
                          type="link"
                          danger
                          onClick={() => handleRemoveFavorite(item.case_id)}
                        >
                          取消收藏
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <a onClick={() => navigate(`/case/${item.case_id}`)}>
                            {caseInfo.title}
                          </a>
                        }
                        description={
                          <Space direction="vertical" size="small">
                            <Space>
                              <Tag color="blue">{caseInfo.case_type}</Tag>
                              <Tag>{caseInfo.court}</Tag>
                              <span>{caseInfo.judgment_date}</span>
                            </Space>
                            <span style={{ fontSize: 12, color: '#999' }}>
                              收藏于 {new Date(item.created_at).toLocaleString('zh-CN')}
                            </span>
                          </Space>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            )}
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default MyFavorites;
