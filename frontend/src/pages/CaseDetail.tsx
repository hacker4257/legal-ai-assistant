import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Card, Button, Descriptions, Typography, Space, Spin, message, Divider, Collapse, Tag, Alert, Segmented, Dropdown, Input, Modal, List } from 'antd';
import { ArrowLeftOutlined, ThunderboltOutlined, FileTextOutlined, TeamOutlined, BankOutlined, CheckCircleOutlined, UserOutlined, SafetyOutlined, DownloadOutlined, StarOutlined, StarFilled, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { casesAPI, favoritesAPI } from '../api';

const { Header, Content } = Layout;
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
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!caseData) {
    return <div>案例不存在</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#fff', padding: '0 50px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', position: 'sticky', top: 0, zIndex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>法律 AI 助手</Title>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>
            返回
          </Button>
        </div>
      </Header>

      <Content style={{ padding: '24px 50px', maxWidth: '100%', width: '100%' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto', width: '100%' }}>
          <Card>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Title level={2}>{caseData.title}</Title>
                <Descriptions column={2}>
                  <Descriptions.Item label="案号">{caseData.case_number}</Descriptions.Item>
                  <Descriptions.Item label="法院">{caseData.court}</Descriptions.Item>
                  <Descriptions.Item label="案件类型">{caseData.case_type}</Descriptions.Item>
                  <Descriptions.Item label="判决日期">{caseData.judgment_date}</Descriptions.Item>
                </Descriptions>
              </div>

              <div>
                <Space>
                  <Button
                    type="primary"
                    icon={<ThunderboltOutlined />}
                    onClick={handleAnalyze}
                    loading={analyzing}
                    size="large"
                  >
                    AI 智能分析
                  </Button>

                  {analysis && (
                    <>
                      <Button
                        icon={isFavorited ? <StarFilled /> : <StarOutlined />}
                        onClick={handleToggleFavorite}
                        size="large"
                        style={{ color: isFavorited ? '#faad14' : undefined }}
                      >
                        {isFavorited ? '已收藏' : '收藏'}
                      </Button>

                      <Button
                        icon={<EditOutlined />}
                        onClick={handleAddNote}
                        size="large"
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
                      >
                        导出 PDF
                      </Button>
                    </Dropdown>
                    </>
                  )}
                </Space>
              </div>

              {analysis && (
                <Card
                  title={
                    <Space>
                      <ThunderboltOutlined style={{ color: '#1890ff' }} />
                      <span>AI 智能分析报告</span>
                      <Tag color="success">分析完成</Tag>
                    </Space>
                  }
                  extra={
                    <Segmented
                      size="large"
                      options={[
                        {
                          label: (
                            <Space>
                              <UserOutlined />
                              <span style={{ fontWeight: 500 }}>普通人视角</span>
                            </Space>
                          ),
                          value: 'plain',
                        },
                        {
                          label: (
                            <Space>
                              <SafetyOutlined />
                              <span style={{ fontWeight: 500 }}>专业视角</span>
                            </Space>
                          ),
                          value: 'professional',
                        },
                      ]}
                      value={viewMode}
                      onChange={(value) => setViewMode(value as 'professional' | 'plain')}
                      style={{
                        background: '#fff',
                        padding: '4px',
                        borderRadius: '8px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                      }}
                    />
                  }
                  style={{ background: '#fafafa' }}
                >
                  <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    {/* 案情摘要 */}
                    <Alert
                      message={viewMode === 'plain' ? '这个案子讲的是什么？' : '案情摘要'}
                      description={
                        <Text style={{ fontSize: '15px', lineHeight: '1.8' }}>
                          {viewMode === 'plain' && analysis.summary_plain
                            ? analysis.summary_plain
                            : analysis.summary}
                        </Text>
                      }
                      type="info"
                      showIcon
                      icon={<FileTextOutlined />}
                    />

                    {/* 关键要素 */}
                    <Card
                      size="small"
                      title={
                        <Space>
                          <TeamOutlined />
                          <span>{viewMode === 'plain' ? '案件基本情况' : '关键要素'}</span>
                        </Space>
                      }
                      style={{ background: '#fff' }}
                    >
                      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                        {viewMode === 'plain' && analysis.key_elements_plain ? (
                          <>
                            {analysis.key_elements_plain.who && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>👥 谁告谁？</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements_plain.who}
                                </Paragraph>
                              </div>
                            )}
                            {analysis.key_elements_plain.what_happened && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>📋 发生了什么？</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements_plain.what_happened}
                                </Paragraph>
                              </div>
                            )}
                            {analysis.key_elements_plain.what_they_want && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>⚖️ 双方的诉求</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements_plain.what_they_want}
                                </Paragraph>
                              </div>
                            )}
                          </>
                        ) : (
                          <>
                            {analysis.key_elements.parties && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>👥 当事人信息</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements.parties}
                                </Paragraph>
                              </div>
                            )}
                            {analysis.key_elements.case_cause && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>📋 案由</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements.case_cause}
                                </Paragraph>
                              </div>
                            )}
                            {analysis.key_elements.dispute_focus && (
                              <div>
                                <Text strong style={{ color: '#1890ff' }}>⚖️ 争议焦点</Text>
                                <Paragraph style={{ marginTop: 8, marginLeft: 20, lineHeight: '1.8' }}>
                                  {analysis.key_elements.dispute_focus}
                                </Paragraph>
                              </div>
                            )}
                          </>
                        )}
                      </Space>
                    </Card>

                    {/* 判决理由 */}
                    <Collapse defaultActiveKey={['1']} ghost>
                      <Panel
                        header={
                          <Text strong style={{ fontSize: '16px' }}>
                            <BankOutlined /> {viewMode === 'plain' ? '法院为什么这么判？' : '判决理由分析'}
                          </Text>
                        }
                        key="1"
                      >
                        <Card size="small" style={{ background: '#fff' }}>
                          <Paragraph style={{ fontSize: '15px', lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
                            {viewMode === 'plain' && analysis.legal_reasoning_plain
                              ? analysis.legal_reasoning_plain
                              : analysis.legal_reasoning}
                          </Paragraph>
                        </Card>
                      </Panel>
                    </Collapse>

                    {/* 法律依据 */}
                    <Card
                      size="small"
                      title={
                        <Space>
                          <CheckCircleOutlined />
                          <span>{viewMode === 'plain' ? '相关法律规定' : '法律依据'}</span>
                        </Space>
                      }
                      style={{ background: '#fff' }}
                    >
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        {(viewMode === 'plain' && analysis.legal_basis_plain
                          ? analysis.legal_basis_plain
                          : analysis.legal_basis
                        ).map((basis, index) => (
                          <Card
                            key={index}
                            size="small"
                            style={{
                              background: viewMode === 'plain' ? '#fff7e6' : '#f0f5ff',
                              borderLeft: `3px solid ${viewMode === 'plain' ? '#fa8c16' : '#1890ff'}`,
                              marginBottom: 8
                            }}
                          >
                            <Space align="start" style={{ width: '100%' }}>
                              <Tag color={viewMode === 'plain' ? 'orange' : 'blue'}>{index + 1}</Tag>
                              <div style={{ flex: 1 }}>
                                <Text style={{ fontSize: '14px', lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
                                  {basis}
                                </Text>
                              </div>
                            </Space>
                          </Card>
                        ))}
                      </Space>
                    </Card>

                    {/* 裁判结果 */}
                    {(viewMode === 'plain' ? analysis.judgment_result_plain : analysis.judgment_result) && (
                      <Alert
                        message={viewMode === 'plain' ? '最终结果' : '裁判结果'}
                        description={
                          <Text style={{ fontSize: '15px', lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
                            {viewMode === 'plain' && analysis.judgment_result_plain
                              ? analysis.judgment_result_plain
                              : analysis.judgment_result}
                          </Text>
                        }
                        type="success"
                        showIcon
                        icon={<CheckCircleOutlined />}
                      />
                    )}

                    {/* 普通人建议 - 仅在通俗版显示 */}
                    {viewMode === 'plain' && analysis.plain_language_tips && (
                      <Alert
                        message="💡 给你的建议"
                        description={
                          <div
                            style={{
                              fontSize: '15px',
                              lineHeight: '1.8',
                            }}
                            className="markdown-content"
                          >
                            <ReactMarkdown
                              components={{
                                p: ({node, ...props}) => <p style={{ marginBottom: '12px' }} {...props} />,
                                strong: ({node, ...props}) => <strong style={{ color: '#d46b08', fontWeight: 600 }} {...props} />,
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
                      />
                    )}
                  </Space>
                </Card>
              )}

              {/* 笔记区域 */}
              {notes.length > 0 && (
                <Card title={<Space><EditOutlined /> 我的笔记</Space>}>
                  <List
                    dataSource={notes}
                    renderItem={(note: any) => (
                      <List.Item
                        actions={[
                          <Button
                            type="link"
                            icon={<EditOutlined />}
                            onClick={() => handleEditNote(note)}
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
                              <div style={{ marginBottom: 8 }}>{note.content}</div>
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

              <Collapse defaultActiveKey={[]} ghost>
                <Panel
                  header={
                    <Text strong style={{ fontSize: '16px' }}>
                      <FileTextOutlined /> 判决书全文
                    </Text>
                  }
                  key="1"
                >
                  <Card>
                    <Paragraph style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8' }}>
                      {caseData.content}
                    </Paragraph>
                  </Card>
                </Panel>
              </Collapse>
            </Space>
          </Card>
        </div>
      </Content>

      {/* 笔记模态框 */}
      <Modal
        title={editingNoteId ? '编辑笔记' : '添加笔记'}
        open={noteModalVisible}
        onOk={handleSaveNote}
        onCancel={() => {
          setNoteModalVisible(false);
          setNoteContent('');
          setEditingNoteId(null);
        }}
        okText="保存"
        cancelText="取消"
      >
        <Input.TextArea
          rows={6}
          value={noteContent}
          onChange={(e) => setNoteContent(e.target.value)}
          placeholder="输入你的笔记..."
        />
      </Modal>
    </Layout>
  );
};

export default CaseDetail;
