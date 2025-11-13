/**
 * 私有路由组件 - 需要登录才能访问
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface PrivateRouteProps {
  children: React.ReactElement;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { checkAuth } = useAuthStore();
  
  if (!checkAuth()) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

export default PrivateRoute;
