import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Card, Button, Descriptions, Typography, Space, message, Collapse, Tag, Alert, Segmented, Dropdown, Input, Modal, List, Row, Col } from 'antd';
import { ArrowLeftOutlined, ThunderboltOutlined, FileTextOutlined, TeamOutlined, BankOutlined, CheckCircleOutlined, UserOutlined, DownloadOutlined, StarOutlined, StarFilled, EditOutlined, DeleteOutlined, BookOutlined, RobotOutlined, LinkOutlined, CalendarOutlined, AuditOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { casesAPI, favoritesAPI } from '../api';
import ScaleIcon from '../components/ScaleIcon';
import PageHeader from '../components/PageHeader';
import Loading from '../components/Loading';
import theme from '../styles/theme';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

interface CaseDetail {
  id: number;
  case_number: string;
  title: string;
  court: string;
  case_type: string;
  judgment_date: string;
  content: string;
  parties: any;
  legal_basis: any;
}

interface CitationInfo {
  type: 'statute' | 'case' | 'interpretation';
  id: number;
  title: string;
  relevance_score: number;
}

interface AgentMetadata {
  steps_executed: string[];
  similar_cases_found: number;
  legal_basis_found: number;
  rag_enabled: boolean;
  statutes_retrieved: number;
}

interface Analysis {
  summary: string;
  summary_plain?: string;
  key_elements: {
    parties?: string;
    case_cause?: string;
    dispute_focus?: string;
  };
  key_elements_plain?: {
    who?: string;
    what_happened?: string;
    what_they_want?: string;
  };
  legal_reasoning: string;
  legal_reasoning_plain?: string;
  legal_basis: string[];
  legal_basis_plain?: string[];
  judgment_result: string;
  judgment_result_plain?: string;
  plain_language_tips?: string;
  // RAG 增强字段
  citations?: CitationInfo[];
  agent_metadata?: AgentMetadata;
}

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [viewMode, setViewMode] = useState<'professional' | 'plain'>('plain'); // 默认显示通俗版

  // 收藏和笔记相关
  const [isFavorited, setIsFavorited] = useState(false);
  const [notes, setNotes] = useState<any[]>([]);
  const [noteModalVisible, setNoteModalVisible] = useState(false);
  const [noteContent, setNoteContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);

  useEffect(() => {
    fetchCase();
    checkFavorite();
    fetchNotes();
  }, [id]);

  const fetchCase = async () => {
    try {
      const response = await casesAPI.getCase(Number(id));
      setCaseData(response.data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取案例失败');
    } finally {
      setLoading(false);
    }
  };

  const checkFavorite = async () => {
    try {
      const response = await favoritesAPI.checkFavorite(Number(id));
      setIsFavorited(response.data.is_favorited);
    } catch (error) {
      console.error('检查收藏状态失败:', error);
    }
  };

  const fetchNotes = async () => {
    try {
      const response = await favoritesAPI.getNotes(Number(id));
      setNotes(response.data);
    } catch (error) {
      console.error('获取笔记失败:', error);
    }
  };

  const handleToggleFavorite = async () => {
    try {
      if (isFavorited) {
        await favoritesAPI.removeFavorite(Number(id));
        message.success('已取消收藏');
        setIsFavorited(false);
      } else {
        await favoritesAPI.addFavorite(Number(id));
        message.success('收藏成功');
        setIsFavorited(true);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleAddNote = () => {
    setEditingNoteId(null);
    setNoteContent('');
    setNoteModalVisible(true);
  };

  const handleEditNote = (note: any) => {
    setEditingNoteId(note.id);
    setNoteContent(note.content);
    setNoteModalVisible(true);
  };

  const handleSaveNote = async () => {
    if (!noteContent.trim()) {
      message.warning('请输入笔记内容');
      return;
    }

    try {
      if (editingNoteId) {
        await favoritesAPI.updateNote(editingNoteId, noteContent);
        message.success('笔记已更新');
      } else {
        await favoritesAPI.createNote({ case_id: Number(id), content: noteContent });
        message.success('笔记已添加');
      }
      setNoteModalVisible(false);
      setNoteContent('');
      setEditingNoteId(null);
      fetchNotes();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      await favoritesAPI.deleteNote(noteId);
      message.success('笔记已删除');
      fetchNotes();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const response = await casesAPI.analyzeCase(Number(id));
      setAnalysis(response.data);

      // 调试：打印收到的数据
      console.log('收到的分析数据:', response.data);
      console.log('summary:', response.data.summary?.substring(0, 50));
      console.log('summary_plain:', response.data.summary_plain?.substring(0, 50));
      console.log('是否相同:', response.data.summary === response.data.summary_plain);

      message.success('分析完成！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '分析失败');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleExportPDF = async (perspective: 'both' | 'professional' | 'plain') => {
    if (!analysis) {
      message.warning('请先进行 AI 分析');
      return;
    }

    setExporting(true);
    try {
      const response = await casesAPI.exportPDF(Number(id), perspective);

      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      const perspectiveName = {
        both: '双视角',
        professional: '专业版',
        plain: '普通人版'
      };
      link.setAttribute('download', `${caseData?.case_number}_${perspectiveName[perspective]}_分析报告.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      message.success('PDF 导出成功！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导出失败');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <Loading fullscreen tip="加载案例详情..." />;
  }

  if (!caseData) {
    return <div>案例不存在</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh', background: theme.colors.background.secondary }}>
      <PageHeader
        title="法律 AI 助手"
        showBackButton
      />

      <Content style={{ padding: '32px 40px' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto' }}>
          {/* 案例基本信息卡片 */}
          <Card
            style={{
              borderRadius: theme.borderRadius['2xl'],
              border: `1px solid ${theme.colors.border.light}`,
              boxShadow: theme.shadows.card,
              marginBottom: 24,
            }}
            styles={{ body: { padding: 32 } }}
          >
            <Space direction="vertical" size={24} style={{ width: '100%' }}>
              {/* 标题区域 */}
              <div>
                <Title level={2} style={{ marginBottom: 16, color: theme.colors.text.primary }}>
                  {caseData.title}
                </Title>

                <Row gutter={[24, 16]}>
                  <Col xs={24} sm={12} md={6}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <AuditOutlined style={{ color: theme.colors.primary }} />
                      <Text type="secondary">案号</Text>
                    </div>
                    <Text strong style={{ display: 'block', marginTop: 4, fontSize: 15 }}>
                      {caseData.case_number}
                    </Text>
                  </Col>
                  <Col xs={24} sm={12} md={6}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <BankOutlined style={{ color: theme.colors.primary }} />
                      <Text type="secondary">法院</Text>
                    </div>
                    <Text strong style={{ display: 'block', marginTop: 4, fontSize: 15 }}>
                      {caseData.court}
                    </Text>
                  </Col>
                  <Col xs={24} sm={12} md={6}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <FileTextOutlined style={{ color: theme.colors.primary }} />
                      <Text type="secondary">案件类型</Text>
                    </div>
                    <Tag
                      color="blue"
                      style={{
                        marginTop: 4,
                        borderRadius: theme.borderRadius.small,
                        padding: '2px 12px',
                      }}
                    >
                      {caseData.case_type}
                    </Tag>
                  </Col>
                  <Col xs={24} sm={12} md={6}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <CalendarOutlined style={{ color: theme.colors.primary }} />
                      <Text type="secondary">判决日期</Text>
                    </div>
                    <Text strong style={{ display: 'block', marginTop: 4, fontSize: 15 }}>
                      {caseData.judgment_date}
                    </Text>
                  </Col>
                </Row>
              </div>

              {/* 操作按钮 */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 12,
                paddingTop: 16,
                borderTop: `1px solid ${theme.colors.border.light}`,
              }}>
                <Button
                  type="primary"
                  icon={<ThunderboltOutlined />}
                  onClick={handleAnalyze}
                  loading={analyzing}
                  size="large"
                  style={{
                    borderRadius: theme.borderRadius.medium,
                    height: 44,
                    paddingLeft: 24,
                    paddingRight: 24,
                    fontWeight: 500,
                  }}
                >
                  {analyzing ? 'AI 分析中...' : 'AI 智能分析'}
                </Button>

                {analysis && (
                  <>
                    <Button
                      icon={isFavorited ? <StarFilled /> : <StarOutlined />}
                      onClick={handleToggleFavorite}
                      size="large"
                      style={{
                        borderRadius: theme.borderRadius.medium,
                        height: 44,
                        color: isFavorited ? theme.colors.accent : undefined,
                        borderColor: isFavorited ? theme.colors.accent : theme.colors.border.light,
                      }}
                    >
                      {isFavorited ? '已收藏' : '收藏'}
                    </Button>

                    <Button
                      icon={<EditOutlined />}
                      onClick={handleAddNote}
                      size="large"
                      style={{
                        borderRadius: theme.borderRadius.medium,
                        height: 44,
                        borderColor: theme.colors.border.light,
                      }}
                    >
                      添加笔记
                    </Button>

                    <Dropdown
                      menu={{
                        items: [
                          {
                            key: 'both',
                            label: '导出双视角版',
                            onClick: () => handleExportPDF('both'),
                          },
                          {
                            key: 'plain',
                            label: '导出普通人版',
                            onClick: () => handleExportPDF('plain'),
                          },
                          {
                            key: 'professional',
                            label: '导出专业版',
                            onClick: () => handleExportPDF('professional'),
                          },
                        ],
                      }}
                    >
                      <Button
                        icon={<DownloadOutlined />}
                        loading={exporting}
                        size="large"
                        style={{
                          borderRadius: theme.borderRadius.medium,
                          height: 44,
                          borderColor: theme.colors.border.light,
                        }}
                      >
                        导出 PDF
                      </Button>
                    </Dropdown>
                  </>
                )}
              </div>
            </Space>
          </Card>

          {/* AI 分析报告卡片 */}
          {analysis && (
            <Card
              style={{
                borderRadius: theme.borderRadius['2xl'],
                border: `1px solid ${theme.colors.border.light}`,
                boxShadow: theme.shadows.card,
                marginBottom: 24,
                overflow: 'hidden',
              }}
              styles={{ body: { padding: 0 } }}
            >
              {/* 分析报告头部 */}
              <div style={{
                background: theme.colors.gradientHero,
                padding: '24px 32px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 16,
              }}>
                <Space>
                  <ThunderboltOutlined style={{ color: theme.colors.accent, fontSize: 24 }} />
                  <Title level={4} style={{ margin: 0, color: '#fff' }}>
                    AI 智能分析报告
                  </Title>
                  <Tag color="success" style={{ borderRadius: 4 }}>分析完成</Tag>
                  {analysis.agent_metadata?.rag_enabled && (
                    <Tag color="gold" style={{ borderRadius: 4 }}>RAG 增强</Tag>
                  )}
                </Space>

                <Segmented
                  size="large"
                  options={[
                    {
                      label: (
                        <Space style={{ padding: '4px 8px' }}>
                          <UserOutlined />
                          <span style={{ fontWeight: 500 }}>普通人视角</span>
                        </Space>
                      ),
                      value: 'plain',
                    },
                    {
                      label: (
                        <Space style={{ padding: '4px 8px' }}>
                          <ScaleIcon />
                          <span style={{ fontWeight: 500 }}>专业视角</span>
                        </Space>
                      ),
                      value: 'professional',
                    },
                  ]}
                  value={viewMode}
                  onChange={(value) => setViewMode(value as 'professional' | 'plain')}
                />
              </div>

              {/* 分析内容 */}
              <div style={{ padding: 32 }}>
                <Space direction="vertical" size={24} style={{ width: '100%' }}>
                  {/* 案情摘要 */}
                  <Alert
                    message={
                      <Text strong style={{ fontSize: 16 }}>
                        {viewMode === 'plain' ? '这个案子讲的是什么？' : '案情摘要'}
                      </Text>
                    }
                    description={
                      <Text style={{ fontSize: 15, lineHeight: 1.8 }}>
                        {viewMode === 'plain' && analysis.summary_plain
                          ? analysis.summary_plain
                          : analysis.summary}
                      </Text>
                    }
                    type="info"
                    showIcon
                    icon={<FileTextOutlined />}
                    style={{ borderRadius: theme.borderRadius.large }}
                  />

                  {/* 关键要素 */}
                  <Card
                    size="small"
                    title={
                      <Space>
                        <TeamOutlined style={{ color: theme.colors.primary }} />
                        <span style={{ fontWeight: 600 }}>
                          {viewMode === 'plain' ? '案件基本情况' : '关键要素'}
                        </span>
                      </Space>
                    }
                    style={{
                      borderRadius: theme.borderRadius.large,
                      border: `1px solid ${theme.colors.border.light}`,
                    }}
                  >
                    <Space direction="vertical" size={16} style={{ width: '100%' }}>
                      {viewMode === 'plain' && analysis.key_elements_plain ? (
                        <>
                          {analysis.key_elements_plain.who && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                👥 谁告谁？
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements_plain.who}
                              </Paragraph>
                            </div>
                          )}
                          {analysis.key_elements_plain.what_happened && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                📋 发生了什么？
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements_plain.what_happened}
                              </Paragraph>
                            </div>
                          )}
                          {analysis.key_elements_plain.what_they_want && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                ⚖️ 双方的诉求
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements_plain.what_they_want}
                              </Paragraph>
                            </div>
                          )}
                        </>
                      ) : (
                        <>
                          {analysis.key_elements.parties && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                👥 当事人信息
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements.parties}
                              </Paragraph>
                            </div>
                          )}
                          {analysis.key_elements.case_cause && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                📋 案由
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements.case_cause}
                              </Paragraph>
                            </div>
                          )}
                          {analysis.key_elements.dispute_focus && (
                            <div style={{
                              padding: 16,
                              background: theme.colors.background.tertiary,
                              borderRadius: theme.borderRadius.medium,
                            }}>
                              <Text strong style={{ color: theme.colors.primary, fontSize: 15 }}>
                                ⚖️ 争议焦点
                              </Text>
                              <Paragraph style={{ marginTop: 8, marginBottom: 0, lineHeight: 1.8 }}>
                                {analysis.key_elements.dispute_focus}
                              </Paragraph>
                            </div>
                          )}
                        </>
                      )}
                    </Space>
                  </Card>

                  {/* 判决理由 */}
                  <Collapse
                    defaultActiveKey={['1']}
                    style={{
                      borderRadius: theme.borderRadius.large,
                      border: `1px solid ${theme.colors.border.light}`,
                    }}
                  >
                    <Panel
                      header={
                        <Space>
                          <BankOutlined style={{ color: theme.colors.primary }} />
                          <Text strong style={{ fontSize: 15 }}>
                            {viewMode === 'plain' ? '法院为什么这么判？' : '判决理由分析'}
                          </Text>
                        </Space>
                      }
                      key="1"
                    >
                      <Paragraph style={{ fontSize: 15, lineHeight: 1.8, whiteSpace: 'pre-wrap', marginBottom: 0 }}>
                        {viewMode === 'plain' && analysis.legal_reasoning_plain
                          ? analysis.legal_reasoning_plain
                          : analysis.legal_reasoning}
                      </Paragraph>
                    </Panel>
                  </Collapse>

                  {/* 法律依据 */}
                  <Collapse
                    defaultActiveKey={['legal_basis']}
                    style={{
                      borderRadius: theme.borderRadius.large,
                      border: `1px solid ${theme.colors.border.light}`,
                    }}
                  >
                    <Panel
                      header={
                        <Space>
                          <BookOutlined style={{ color: theme.colors.primary }} />
                          <Text strong style={{ fontSize: 15 }}>
                            {viewMode === 'plain' ? '相关法律规定' : '法律依据'}
                          </Text>
                        </Space>
                      }
                      key="legal_basis"
                    >
                      <Space direction="vertical" size={12} style={{ width: '100%' }}>
                        {(viewMode === 'plain' && analysis.legal_basis_plain
                          ? analysis.legal_basis_plain
                          : analysis.legal_basis
                        ).map((basis, index) => (
                          <div
                            key={index}
                            style={{
                              padding: 16,
                              background: viewMode === 'plain'
                                ? theme.colors.warningLight
                                : theme.colors.infoLight,
                              borderRadius: theme.borderRadius.medium,
                              borderLeft: `4px solid ${viewMode === 'plain'
                                ? theme.colors.warning
                                : theme.colors.info}`,
                            }}
                          >
                            <Space align="start" style={{ width: '100%' }}>
                              <Tag
                                color={viewMode === 'plain' ? 'orange' : 'blue'}
                                style={{ borderRadius: 4, fontWeight: 600 }}
                              >
                                {index + 1}
                              </Tag>
                              <Text style={{ fontSize: 14, lineHeight: 1.8, flex: 1 }}>
                                {basis}
                              </Text>
                            </Space>
                          </div>
                        ))}
                      </Space>
                    </Panel>
                  </Collapse>

                  {/* 裁判结果 */}
                  {(viewMode === 'plain' ? analysis.judgment_result_plain : analysis.judgment_result) && (
                    <Alert
                      message={
                        <Text strong style={{ fontSize: 16 }}>
                          {viewMode === 'plain' ? '最终结果' : '裁判结果'}
                        </Text>
                      }
                      description={
                        <div style={{ fontSize: 15, lineHeight: 1.8 }} className="markdown-content">
                          <ReactMarkdown
                            components={{
                              p: ({node, ...props}) => <p style={{ marginBottom: '12px' }} {...props} />,
                              strong: ({node, ...props}) => <strong style={{ color: theme.colors.accentDark, fontWeight: 600 }} {...props} />,
                              ol: ({node, ...props}) => <ol style={{ paddingLeft: '20px', marginBottom: '12px' }} {...props} />,
                              ul: ({node, ...props}) => <ul style={{ paddingLeft: '20px', marginBottom: '12px' }} {...props} />,
                              li: ({node, ...props}) => <li style={{ marginBottom: '8px' }} {...props} />,
                            }}
                          >
                            {viewMode === 'plain' && analysis.judgment_result_plain
                              ? analysis.judgment_result_plain
                              : analysis.judgment_result}
                          </ReactMarkdown>
                        </div>
                      }
                      type="success"
                      showIcon
                      icon={<CheckCircleOutlined />}
                      style={{ borderRadius: theme.borderRadius.large }}
                    />
                  )}

                  {/* 普通人建议 - 仅在通俗版显示 */}
                  {viewMode === 'plain' && analysis.plain_language_tips && (
                    <Alert
                      message={
                        <Text strong style={{ fontSize: 16 }}>💡 给你的建议</Text>
                      }
                      description={
                        <div style={{ fontSize: 15, lineHeight: 1.8 }} className="markdown-content">
                          <ReactMarkdown
                            components={{
                              p: ({node, ...props}) => <p style={{ marginBottom: '12px' }} {...props} />,
                              strong: ({node, ...props}) => <strong style={{ color: theme.colors.accentDark, fontWeight: 600 }} {...props} />,
                              ol: ({node, ...props}) => <ol style={{ paddingLeft: '20px', marginBottom: '12px' }} {...props} />,
                              ul: ({node, ...props}) => <ul style={{ paddingLeft: '20px', marginBottom: '12px' }} {...props} />,
                              li: ({node, ...props}) => <li style={{ marginBottom: '8px' }} {...props} />,
                            }}
                          >
                            {analysis.plain_language_tips}
                          </ReactMarkdown>
                        </div>
                      }
                      type="warning"
                      showIcon
                      style={{ borderRadius: theme.borderRadius.large }}
                    />
                  )}

                  {/* RAG 引用溯源 */}
                  {analysis.citations && analysis.citations.length > 0 && (
                    <Collapse
                      style={{
                        borderRadius: theme.borderRadius.large,
                        border: `1px solid ${theme.colors.border.light}`,
                      }}
                    >
                      <Panel
                        header={
                          <Space>
                            <LinkOutlined style={{ color: theme.colors.success }} />
                            <Text strong style={{ fontSize: 15 }}>
                              引用来源（{analysis.citations.length} 条）
                            </Text>
                          </Space>
                        }
                        key="citations"
                      >
                        <Space direction="vertical" size={12} style={{ width: '100%' }}>
                          {analysis.citations.map((citation, index) => (
                            <div
                              key={index}
                              style={{
                                padding: 16,
                                background: citation.type === 'statute' ? theme.colors.successLight :
                                           citation.type === 'case' ? theme.colors.infoLight : theme.colors.warningLight,
                                borderRadius: theme.borderRadius.medium,
                                borderLeft: `4px solid ${
                                  citation.type === 'statute' ? theme.colors.success :
                                  citation.type === 'case' ? theme.colors.info : theme.colors.warning
                                }`,
                              }}
                            >
                              <Space align="start" style={{ width: '100%' }}>
                                <Tag
                                  color={
                                    citation.type === 'statute' ? 'green' :
                                    citation.type === 'case' ? 'blue' : 'orange'
                                  }
                                  style={{ borderRadius: 4 }}
                                >
                                  {citation.type === 'statute' ? '法条' :
                                   citation.type === 'case' ? '案例' : '司法解释'}
                                </Tag>
                                <div style={{ flex: 1 }}>
                                  <Text strong>{citation.title}</Text>
                                  <div style={{ marginTop: 4 }}>
                                    <Text type="secondary" style={{ fontSize: 12 }}>
                                      相关度: {(citation.relevance_score * 100).toFixed(1)}%
                                    </Text>
                                  </div>
                                </div>
                              </Space>
                            </div>
                          ))}
                        </Space>
                      </Panel>
                    </Collapse>
                  )}

                  {/* Agent 执行信息 */}
                  {analysis.agent_metadata && (
                    <Card
                      size="small"
                      style={{
                        borderRadius: theme.borderRadius.medium,
                        background: theme.colors.background.tertiary,
                        border: 'none',
                      }}
                    >
                      <Space wrap size={12}>
                        <Tag icon={<RobotOutlined />} color="purple" style={{ borderRadius: 4 }}>AI Agent</Tag>
                        {analysis.agent_metadata.rag_enabled && (
                          <Tag color="green" style={{ borderRadius: 4 }}>RAG 知识库检索</Tag>
                        )}
                        <Text type="secondary" style={{ fontSize: 13 }}>
                          检索法条: {analysis.agent_metadata.statutes_retrieved} 条
                        </Text>
                        <Text type="secondary" style={{ fontSize: 13 }}>
                          相似案例: {analysis.agent_metadata.similar_cases_found} 个
                        </Text>
                        <Text type="secondary" style={{ fontSize: 13 }}>
                          执行步骤: {analysis.agent_metadata.steps_executed?.length || 0}
                        </Text>
                      </Space>
                    </Card>
                  )}
                </Space>
              </div>
            </Card>
          )}

          {/* 笔记区域 */}
          {notes.length > 0 && (
            <Card
              title={
                <Space>
                  <EditOutlined style={{ color: theme.colors.primary }} />
                  <span style={{ fontWeight: 600 }}>我的笔记</span>
                </Space>
              }
              style={{
                borderRadius: theme.borderRadius['2xl'],
                border: `1px solid ${theme.colors.border.light}`,
                boxShadow: theme.shadows.card,
                marginBottom: 24,
              }}
            >
              <List
                dataSource={notes}
                renderItem={(note: any) => (
                  <List.Item
                    style={{
                      padding: '16px 0',
                      borderBottom: `1px solid ${theme.colors.border.light}`,
                    }}
                    actions={[
                      <Button
                        type="link"
                        icon={<EditOutlined />}
                        onClick={() => handleEditNote(note)}
                        style={{ color: theme.colors.primary }}
                      >
                        编辑
                      </Button>,
                      <Button
                        type="link"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleDeleteNote(note.id)}
                      >
                        删除
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      description={
                        <div>
                          <div style={{ marginBottom: 8, fontSize: 15, color: theme.colors.text.primary }}>
                            {note.content}
                          </div>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {new Date(note.created_at).toLocaleString('zh-CN')}
                          </Text>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            </Card>
          )}

          {/* 判决书全文 */}
          <Collapse
            style={{
              borderRadius: theme.borderRadius['2xl'],
              border: `1px solid ${theme.colors.border.light}`,
              boxShadow: theme.shadows.card,
            }}
          >
            <Panel
              header={
                <Space>
                  <FileTextOutlined style={{ color: theme.colors.primary }} />
                  <Text strong style={{ fontSize: 16 }}>判决书全文</Text>
                </Space>
              }
              key="1"
            >
              <Paragraph style={{
                whiteSpace: 'pre-wrap',
                lineHeight: 1.8,
                fontSize: 15,
                color: theme.colors.text.primary,
              }}>
                {caseData.content}
              </Paragraph>
            </Panel>
          </Collapse>
        </div>
      </Content>

      {/* 笔记模态框 */}
      <Modal
        title={
          <Text strong style={{ fontSize: 16 }}>
            {editingNoteId ? '编辑笔记' : '添加笔记'}
          </Text>
        }
        open={noteModalVisible}
        onOk={handleSaveNote}
        onCancel={() => {
          setNoteModalVisible(false);
          setNoteContent('');
          setEditingNoteId(null);
        }}
        okText="保存"
        cancelText="取消"
        styles={{
          body: { padding: '24px 0' },
        }}
      >
        <Input.TextArea
          rows={6}
          value={noteContent}
          onChange={(e) => setNoteContent(e.target.value)}
          placeholder="输入你的笔记..."
          style={{
            borderRadius: theme.borderRadius.medium,
            fontSize: 15,
          }}
        />
      </Modal>
    </Layout>
  );
};

export default CaseDetail;
