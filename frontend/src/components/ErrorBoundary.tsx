import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { CloseCircleOutlined } from '@ant-design/icons';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            background: '#f0f2f5',
          }}
        >
          <Result
            status="error"
            title="出错了"
            subTitle="抱歉，页面发生了错误。请刷新页面重试。"
            icon={<CloseCircleOutlined />}
            extra={[
              <Button type="primary" key="home" onClick={this.handleReset}>
                返回首页
              </Button>,
              <Button key="reload" onClick={() => window.location.reload()}>
                刷新页面
              </Button>,
            ]}
          >
            {this.state.error && (
              <div style={{ marginTop: 16, textAlign: 'left' }}>
                <details style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#666' }}>
                  <summary>错误详情</summary>
                  <p style={{ marginTop: 8 }}>{this.state.error.toString()}</p>
                </details>
              </div>
            )}
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
