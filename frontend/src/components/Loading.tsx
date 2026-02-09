import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import theme from '../styles/theme';

interface LoadingProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
  fullscreen?: boolean;
}

const Loading: React.FC<LoadingProps> = ({
  tip = '加载中...',
  size = 'large',
  fullscreen = false,
}) => {
  const antIcon = (
    <LoadingOutlined
      style={{
        fontSize: size === 'large' ? 48 : 24,
        color: theme.colors.primary,
      }}
      spin
    />
  );

  if (fullscreen) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: theme.colors.background.secondary,
          gap: 20,
        }}
      >
        <Spin indicator={antIcon} size={size} />
        <span style={{ color: theme.colors.text.secondary, fontSize: 15 }}>{tip}</span>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '60px 0',
        gap: 16,
      }}
    >
      <Spin indicator={antIcon} size={size} />
      <span style={{ color: theme.colors.text.secondary, fontSize: 14 }}>{tip}</span>
    </div>
  );
};

export default Loading;
