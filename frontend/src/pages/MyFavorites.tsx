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

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <PageHeader title="我的收藏" showBackButton />
        <Content style={{ padding: '50px' }}>
          <Loading tip="加载收藏列表..." />
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <PageHeader title="我的收藏" showBackButton />

      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
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
            <Card>
              <List
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
            </Card>
          )}
        </div>
      </Content>
    </Layout>
  );
};

export default MyFavorites;
