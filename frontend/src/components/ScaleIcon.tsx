import React from 'react';

interface ScaleIconProps {
  style?: React.CSSProperties;
}

const ScaleIcon: React.FC<ScaleIconProps> = ({ style }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      style={{ width: '1em', height: '1em', ...style }}
    >
      {/* 左边盘子 */}
      <ellipse cx="30" cy="45" rx="12" ry="4" fill="currentColor" opacity="0.9"/>
      <line x1="30" y1="45" x2="30" y2="35" stroke="currentColor" strokeWidth="2"/>

      {/* 右边盘子 */}
      <ellipse cx="70" cy="45" rx="12" ry="4" fill="currentColor" opacity="0.9"/>
      <line x1="70" y1="45" x2="70" y2="35" stroke="currentColor" strokeWidth="2"/>

      {/* 横梁 */}
      <line x1="30" y1="35" x2="70" y2="35" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>

      {/* 中心支柱 */}
      <line x1="50" y1="35" x2="50" y2="65" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>

      {/* 底座 */}
      <rect x="40" y="65" width="20" height="8" rx="2" fill="currentColor" opacity="0.9"/>

      {/* AI 标识 */}
      <text x="50" y="85" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="currentColor" textAnchor="middle">AI</text>
    </svg>
  );
};

export default ScaleIcon;
