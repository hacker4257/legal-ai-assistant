import React from 'react';
import { Empty, Button } from 'antd';
import { FileTextOutlined, SearchOutlined, InboxOutlined } from '@ant-design/icons';

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
    switch (type) {
      case 'search':
        return <SearchOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />;
      case 'upload':
        return <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />;
      default:
        return <FileTextOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />;
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
    <div style={{ padding: '50px 0', textAlign: 'center' }}>
      <Empty
        image={getIcon()}
        description={getDescription()}
        style={{ marginBottom: 24 }}
      >
        {action && (
          <Button type="primary" onClick={action.onClick}>
            {action.text}
          </Button>
        )}
      </Empty>
    </div>
  );
};

export default EmptyState;
