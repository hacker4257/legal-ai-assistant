import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Tabs, Typography, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api';
import { useAuthStore } from '../store/authStore';
import ScaleIcon from '../components/ScaleIcon';
import theme from '../styles/theme';

const { Title, Text, Paragraph } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const onLogin = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const response = await authAPI.login(values.username, values.password);
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);
      const userResponse = await authAPI.getMe();
      login(access_token, userResponse.data);
      message.success('登录成功！');
      navigate('/');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const onRegister = async (values: { username: string; email: string; password: string }) => {
    setLoading(true);
    try {
      await authAPI.register(values);
      message.success('注册成功！请登录');
      setActiveTab('login');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background: theme.colors.background.secondary,
    }}>
      {/* 左侧品牌区域 */}
      <div style={{
        flex: 1,
        background: theme.colors.gradientHero,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 60,
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* 背景装饰 */}
        <div style={{
          position: 'absolute',
          top: -150,
          right: -150,
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: 'rgba(212, 168, 75, 0.08)',
          filter: 'blur(80px)',
        }} />
        <div style={{
          position: 'absolute',
          bottom: -100,
          left: -100,
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'rgba(45, 90, 138, 0.15)',
          filter: 'blur(60px)',
        }} />

        <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', maxWidth: 480 }}>
          {/* Logo */}
          <div style={{
            width: 80,
            height: 80,
            borderRadius: 20,
            background: 'rgba(255,255,255,0.15)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 32px',
            border: '1px solid rgba(255,255,255,0.2)',
          }}>
            <ScaleIcon style={{ fontSize: 44, color: '#fff' }} />
          </div>

          <Title level={1} style={{
            color: '#fff',
            fontSize: 40,
            marginBottom: 16,
            fontWeight: 700,
          }}>
            法律 AI 助手
          </Title>

          <Paragraph style={{
            color: 'rgba(255,255,255,0.75)',
            fontSize: 18,
            lineHeight: 1.8,
            marginBottom: 48,
          }}>
            让法律判决书人人都能看懂
            <br />
            AI 双视角分析 · RAG 增强检索 · 引用可溯源
          </Paragraph>

          {/* 特性列表 */}
          <Space direction="vertical" size={20} style={{ textAlign: 'left' }}>
            {[
              { icon: '🤖', text: 'AI 智能分析，专业版 + 通俗版双视角解读' },
              { icon: '📚', text: '法条知识库检索，每条分析有据可查' },
              { icon: '📄', text: '支持 PDF 上传，一键生成分析报告' },
            ].map((item, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '16px 24px',
                background: 'rgba(255,255,255,0.08)',
                borderRadius: 12,
                backdropFilter: 'blur(10px)',
              }}>
                <span style={{ fontSize: 24 }}>{item.icon}</span>
                <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 15 }}>
                  {item.text}
                </Text>
              </div>
            ))}
          </Space>
        </div>
      </div>

      {/* 右侧登录区域 */}
      <div style={{
        width: 520,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: 60,
        background: '#fff',
      }}>
        <div style={{ maxWidth: 400, margin: '0 auto', width: '100%' }}>
          <div style={{ marginBottom: 40 }}>
            <Title level={2} style={{
              marginBottom: 8,
              fontWeight: 700,
              color: theme.colors.text.primary,
            }}>
              {activeTab === 'login' ? '欢迎回来' : '创建账户'}
            </Title>
            <Text type="secondary" style={{ fontSize: 15 }}>
              {activeTab === 'login'
                ? '登录您的账户以继续使用'
                : '注册新账户开始使用法律 AI 助手'}
            </Text>
          </div>

          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'login',
                label: '登录',
                children: (
                  <Form onFinish={onLogin} autoComplete="off" layout="vertical" size="large">
                    <Form.Item
                      name="username"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input
                        prefix={<UserOutlined style={{ color: theme.colors.text.tertiary }} />}
                        placeholder="用户名"
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[{ required: true, message: '请输入密码' }]}
                    >
                      <Input.Password
                        prefix={<LockOutlined style={{ color: theme.colors.text.tertiary }} />}
                        placeholder="密码"
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      />
                    </Form.Item>

                    <Form.Item style={{ marginBottom: 16 }}>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={loading}
                        block
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                          fontSize: 16,
                          fontWeight: 600,
                        }}
                      >
                        登录
                      </Button>
                    </Form.Item>

                    <div style={{ textAlign: 'center' }}>
                      <Text type="secondary">
                        还没有账户？{' '}
                        <a onClick={() => setActiveTab('register')} style={{ fontWeight: 500 }}>
                          立即注册
                        </a>
                      </Text>
                    </div>
                  </Form>
                ),
              },
              {
                key: 'register',
                label: '注册',
                children: (
                  <Form onFinish={onRegister} autoComplete="off" layout="vertical" size="large">
                    <Form.Item
                      name="username"
                      rules={[{ required: true, message: '请输入用户名' }]}
                    >
                      <Input
                        prefix={<UserOutlined style={{ color: theme.colors.text.tertiary }} />}
                        placeholder="用户名"
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      />
                    </Form.Item>

                    <Form.Item
                      name="email"
                      rules={[
                        { required: true, message: '请输入邮箱' },
                        { type: 'email', message: '请输入有效的邮箱' }
                      ]}
                    >
                      <Input
                        prefix={<MailOutlined style={{ color: theme.colors.text.tertiary }} />}
                        placeholder="邮箱"
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      />
                    </Form.Item>

                    <Form.Item
                      name="password"
                      rules={[
                        { required: true, message: '请输入密码' },
                        { min: 6, message: '密码至少6位' }
                      ]}
                    >
                      <Input.Password
                        prefix={<LockOutlined style={{ color: theme.colors.text.tertiary }} />}
                        placeholder="密码（至少6位）"
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                        }}
                      />
                    </Form.Item>

                    <Form.Item style={{ marginBottom: 16 }}>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={loading}
                        block
                        style={{
                          height: 50,
                          borderRadius: theme.borderRadius.medium,
                          fontSize: 16,
                          fontWeight: 600,
                        }}
                      >
                        注册
                      </Button>
                    </Form.Item>

                    <div style={{ textAlign: 'center' }}>
                      <Text type="secondary">
                        已有账户？{' '}
                        <a onClick={() => setActiveTab('login')} style={{ fontWeight: 500 }}>
                          立即登录
                        </a>
                      </Text>
                    </div>
                  </Form>
                ),
              },
            ]}
          />

          <Divider style={{ marginTop: 40 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>安全登录</Text>
          </Divider>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            color: theme.colors.text.tertiary,
            fontSize: 13,
          }}>
            <SafetyCertificateOutlined />
            <span>数据加密传输，保护您的隐私安全</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
