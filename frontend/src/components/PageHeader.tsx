import React from 'react';
import { Layout, Typography, Button } from 'antd';
import { ArrowLeftOutlined, HomeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import ScaleIcon from './ScaleIcon';
import theme from '../styles/theme';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

interface PageHeaderProps {
  title: string;
  extra?: React.ReactNode;
  showBackButton?: boolean;
  backTo?: string;
  onBack?: () => void;
}

const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  extra,
  showBackButton = false,
  backTo = '/',
  onBack,
}) => {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(backTo);
    }
  };

  return (
    <AntHeader
      style={{
        background: 'rgba(255, 255, 255, 0.98)',
        padding: '0 40px',
        boxShadow: theme.shadows.header,
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: 64,
        lineHeight: '64px',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: 1400,
          margin: '0 auto',
          height: '100%',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          <div
            style={{
              width: theme.logo.size,
              height: theme.logo.size,
              borderRadius: theme.logo.borderRadius,
              background: theme.logo.background,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: theme.logo.boxShadow,
            }}
          >
            <ScaleIcon style={{ fontSize: theme.logo.fontSize, color: '#fff' }} />
          </div>
          <Title
            level={4}
            style={{
              margin: 0,
              ...theme.title,
              fontSize: 20,
            }}
          >
            {title}
          </Title>
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          {extra}
          {showBackButton && (
            <Button
              icon={backTo === '/' ? <HomeOutlined /> : <ArrowLeftOutlined />}
              onClick={handleBack}
              style={{
                borderRadius: theme.borderRadius.medium,
                height: 40,
                border: `1px solid ${theme.colors.border.light}`,
              }}
            >
              {backTo === '/' ? '返回首页' : '返回'}
            </Button>
          )}
        </div>
      </div>
    </AntHeader>
  );
};

export default PageHeader;
