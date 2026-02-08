import React from 'react';
import { Layout, Typography, Button } from 'antd';
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
        background: theme.colors.background.white,
        padding: '0 50px',
        boxShadow: theme.shadows.header,
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
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
            level={3}
            style={{
              margin: 0,
              ...theme.title,
            }}
          >
            {title}
          </Title>
        </div>

        <div style={{ display: 'flex', gap: 12 }}>
          {extra}
          {showBackButton && (
            <Button onClick={handleBack}>
              返回{backTo === '/' ? '首页' : ''}
            </Button>
          )}
        </div>
      </div>
    </AntHeader>
  );
};

export default PageHeader;
