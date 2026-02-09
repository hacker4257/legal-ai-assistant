import React from 'react';
import { Empty, Button } from 'antd';
import { FileTextOutlined, SearchOutlined, InboxOutlined } from '@ant-design/icons';
import theme from '../styles/theme';

interface EmptyStateProps {
  type?: 'search' | 'data' | 'upload';
  description?: string;
  action?: {
    text: string;
    onClick: () => void;
  };
}

const EmptyState: React.FC<EmptyStateProps> = ({ type = 'data', description, action }) => {
  const getIcon = () => {
    const iconStyle = { fontSize: 72, color: theme.colors.border.medium };
    switch (type) {
      case 'search':
        return <SearchOutlined style={iconStyle} />;
      case 'upload':
        return <InboxOutlined style={iconStyle} />;
      default:
        return <FileTextOutlined style={iconStyle} />;
    }
  };

  const getDescription = () => {
    if (description) return description;
    switch (type) {
      case 'search':
        return '没有找到相关案例，试试其他关键词';
      case 'upload':
        return '还没有上传任何文书';
      default:
        return '暂无数据';
    }
  };

  return (
    <div
      style={{
        padding: '60px 0',
        textAlign: 'center',
        background: theme.colors.background.tertiary,
        borderRadius: theme.borderRadius.xlarge,
      }}
    >
      <Empty
        image={getIcon()}
        description={
          <span style={{ color: theme.colors.text.secondary, fontSize: 15 }}>
            {getDescription()}
          </span>
        }
        style={{ marginBottom: action ? 24 : 0 }}
      >
        {action && (
          <Button
            type="primary"
            onClick={action.onClick}
            style={{
              borderRadius: theme.borderRadius.medium,
              height: 40,
              paddingLeft: 24,
              paddingRight: 24,
            }}
          >
            {action.text}
          </Button>
        )}
      </Empty>
    </div>
  );
};

export default EmptyState;
