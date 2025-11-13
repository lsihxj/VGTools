/**
 * 主控制面板
 */
import React from 'react';
import { Layout, Menu, Button } from 'antd';
import {
  ProjectOutlined,
  FileTextOutlined,
  VideoCameraOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={220}>
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'white',
          fontSize: 18,
          fontWeight: 600
        }}>
          AI视频工具
        </div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['projects']}>
          <Menu.Item key="projects" icon={<ProjectOutlined />}>
            我的项目
          </Menu.Item>
          <Menu.Item key="scripts" icon={<FileTextOutlined />}>
            脚本管理
          </Menu.Item>
          <Menu.Item key="videos" icon={<VideoCameraOutlined />}>
            视频制作
          </Menu.Item>
          <Menu.Item key="settings" icon={<SettingOutlined />}>
            模型配置
          </Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0 }}>我的项目</h2>
          <Button 
            icon={<LogoutOutlined />} 
            onClick={handleLogout}
          >
            退出登录
          </Button>
        </Header>

        <Content style={{ margin: '24px', background: '#fff', padding: 24 }}>
          <p>欢迎使用AI视频制作工具!</p>
        </Content>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
