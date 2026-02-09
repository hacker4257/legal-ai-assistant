/**
 * 法律 AI 助手 - 设计系统 2.0
 *
 * 设计理念：专业、可信、现代
 * - 深蓝色传达专业与信任
 * - 金色点缀体现法律的庄重
 * - 大量留白提升阅读体验
 */

const theme = {
  colors: {
    // 主色 - 深邃蓝（专业、信任）
    primary: '#1e3a5f',
    primaryLight: '#2d5a8a',
    primaryDark: '#0f1f35',

    // 强调色 - 琥珀金（法律、庄重）
    accent: '#d4a84b',
    accentLight: '#e8c778',
    accentDark: '#b8922f',

    // 渐变
    gradient: 'linear-gradient(135deg, #1e3a5f 0%, #2d5a8a 50%, #1e3a5f 100%)',
    gradientAccent: 'linear-gradient(135deg, #d4a84b 0%, #e8c778 100%)',
    gradientSubtle: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
    gradientHero: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e293b 100%)',

    // 语义色
    success: '#059669',
    successLight: '#d1fae5',
    warning: '#d97706',
    warningLight: '#fef3c7',
    error: '#dc2626',
    errorLight: '#fee2e2',
    info: '#0284c7',
    infoLight: '#e0f2fe',

    // 中性色
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
      tertiary: '#94a3b8',
      disabled: '#cbd5e1',
      inverse: '#ffffff',
    },

    background: {
      white: '#ffffff',
      primary: '#ffffff',
      secondary: '#f8fafc',
      tertiary: '#f1f5f9',
      dark: '#1e293b',
      gray: '#f0f2f5',
      light: '#fafafa',
    },

    border: {
      light: '#e2e8f0',
      medium: '#cbd5e1',
      dark: '#94a3b8',
    },

    // 视角颜色（保持兼容）
    professional: {
      primary: '#1e3a5f',
      light: '#f0f7ff',
      border: '#1e3a5f',
    },
    plain: {
      primary: '#d97706',
      light: '#fffbeb',
      border: '#d97706',
    },
  },

  // 阴影系统
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
    glow: '0 0 20px rgba(30, 58, 95, 0.15)',
    glowAccent: '0 0 20px rgba(212, 168, 75, 0.3)',
    card: '0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.04)',
    cardHover: '0 8px 24px rgba(30, 58, 95, 0.12), 0 4px 12px rgba(0, 0, 0, 0.08)',
    button: '0 2px 4px rgba(30, 58, 95, 0.15)',
    header: '0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06)',
    hover: '0 8px 24px rgba(30, 58, 95, 0.12)',
  },

  // 圆角
  borderRadius: {
    none: 0,
    small: 6,
    medium: 10,
    large: 14,
    xlarge: 20,
    '2xl': 24,
    full: 9999,
    logo: 12,
  },

  // 间距
  spacing: {
    xs: 6,
    sm: 12,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    '3xl': 64,
  },

  // 字体
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif',
    fontSize: {
      xs: 12,
      sm: 14,
      base: 16,
      lg: 18,
      xl: 20,
      '2xl': 24,
      '3xl': 30,
      '4xl': 36,
      '5xl': 48,
    },
  },

  // 动画
  transitions: {
    fast: '150ms ease',
    normal: '250ms ease',
    slow: '350ms ease',
    spring: '400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
  },

  // 断点
  breakpoints: {
    xs: 480,
    sm: 576,
    md: 768,
    lg: 992,
    xl: 1200,
    xxl: 1536,
  },

  // Logo 样式
  logo: {
    size: 42,
    fontSize: 22,
    borderRadius: 12,
    background: 'linear-gradient(135deg, #1e3a5f 0%, #2d5a8a 100%)',
    boxShadow: '0 4px 12px rgba(30, 58, 95, 0.25)',
  },

  // 标题样式
  title: {
    background: 'linear-gradient(135deg, #1e3a5f 0%, #2d5a8a 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    fontWeight: 700,
    letterSpacing: '-0.02em',
  },

  // 组件特定样式
  components: {
    card: {
      background: '#ffffff',
      borderRadius: 16,
      border: '1px solid #e2e8f0',
      shadow: '0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.04)',
    },
    input: {
      borderRadius: 10,
      borderColor: '#e2e8f0',
      focusBorderColor: '#1e3a5f',
      focusShadow: '0 0 0 3px rgba(30, 58, 95, 0.1)',
    },
    button: {
      primary: {
        background: 'linear-gradient(135deg, #1e3a5f 0%, #2d5a8a 100%)',
        hoverBackground: 'linear-gradient(135deg, #2d5a8a 0%, #3d6a9a 100%)',
        shadow: '0 2px 4px rgba(30, 58, 95, 0.2)',
      },
      accent: {
        background: 'linear-gradient(135deg, #d4a84b 0%, #e8c778 100%)',
        hoverBackground: 'linear-gradient(135deg, #e8c778 0%, #f0d890 100%)',
        shadow: '0 2px 4px rgba(212, 168, 75, 0.3)',
      }
    }
  }
};

export default theme;
