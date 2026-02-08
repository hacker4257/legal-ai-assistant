// 品牌主题配置
export const theme = {
  // 主色调
  colors: {
    primary: '#667eea',
    primaryDark: '#764ba2',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',

    // 语义颜色
    success: '#52c41a',
    warning: '#faad14',
    error: '#f5222d',
    info: '#1890ff',

    // 中性色
    text: {
      primary: 'rgba(0, 0, 0, 0.85)',
      secondary: 'rgba(0, 0, 0, 0.45)',
      disabled: 'rgba(0, 0, 0, 0.25)',
    },

    background: {
      white: '#ffffff',
      gray: '#f0f2f5',
      light: '#fafafa',
    },

    // 视角颜色
    professional: {
      primary: '#1890ff',
      light: '#f0f5ff',
      border: '#1890ff',
    },
    plain: {
      primary: '#fa8c16',
      light: '#fff7e6',
      border: '#fa8c16',
    },
  },

  // 阴影
  shadows: {
    card: '0 2px 8px rgba(0,0,0,0.1)',
    button: '0 4px 12px rgba(102, 126, 234, 0.3)',
    header: '0 2px 8px rgba(0,0,0,0.1)',
    hover: '0 4px 12px rgba(102, 126, 234, 0.15)',
  },

  // 圆角
  borderRadius: {
    small: 4,
    medium: 8,
    large: 12,
    xlarge: 16,
    logo: 10,
  },

  // 间距
  spacing: {
    xs: 8,
    sm: 12,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },

  // Logo 样式
  logo: {
    size: 40,
    fontSize: 24,
    borderRadius: 10,
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
  },

  // 标题样式
  title: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    fontWeight: 600,
  },

  // 断点（响应式）
  breakpoints: {
    xs: 480,
    sm: 576,
    md: 768,
    lg: 992,
    xl: 1200,
    xxl: 1600,
  },
};

export default theme;
