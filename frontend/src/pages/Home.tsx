import React, { useState } from 'react';
import { Layout, Input, Button, Card, List, Typography, Space, Tag, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../api';

const { Header, Content } = Layout;
const { Title, Paragraph } = Typography;
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
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 50px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>法律 AI 助手</Title>
          <Button onClick={() => navigate('/login')}>退出</Button>
        </div>
      </Header>

      <Content style={{ padding: '50px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div style={{ textAlign: 'center' }}>
                <Title level={2}>智能案例检索</Title>
                <Paragraph type="secondary">
                  输入关键词，快速查找相关法律案例
                </Paragraph>
              </div>

              <Search
                placeholder="例如：劳动合同纠纷、交通事故赔偿..."
                enterButton={<><SearchOutlined /> 搜索</>}
                size="large"
                onSearch={onSearch}
                loading={loading}
              />

              {total > 0 && (
                <div>
                  <Title level={4}>搜索结果（共 {total} 条）</Title>
                  <List
                    dataSource={cases}
                    renderItem={(item) => (
                      <List.Item
                        key={item.id}
                        actions={[
                          <Button type="link" onClick={() => navigate(`/case/${item.id}`)}>
                            查看详情
                          </Button>
                        ]}
                      >
                        <List.Item.Meta
                          title={
                            <Space>
                              <a onClick={() => navigate(`/case/${item.id}`)}>{item.title}</a>
                              {item.is_real === 'real' && (
                                <Tag color="green">真实案例</Tag>
                              )}
                              {item.is_real === 'example' && (
                                <Tag color="orange">教学示例</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size="small">
                              <Space>
                                <Tag color="blue">{item.case_type}</Tag>
                                <Tag>{item.court}</Tag>
                                <span>{item.judgment_date}</span>
                              </Space>
                              {item.source && (
                                <span style={{ fontSize: '12px', color: '#8c8c8c' }}>
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
              )}
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default Home;
