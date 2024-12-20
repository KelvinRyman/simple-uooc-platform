// 路由权限配置
const routePermissions = {
    student: ['/pages/student', '/pages/dashboard.html'],
    teacher: ['/pages/teacher', '/pages/dashboard.html'],
    admin: ['/pages/admin', '/pages/dashboard.html'],
    guest: ['/pages/guest']
};

// 公共路由（所有登录用户可访问）
const authorizedRoutes = [
    '/pages/dashboard.html',
    '/pages/profile.html'
];

// 未授权路由（未登录用户可访问）
const unauthorizedRoutes = [
    '/pages/login.html',
    '/pages/register.html',
    '/pages/guest_login.html'
];

// 权限检查工具类
class AuthService {
    // 获取当前用户信息
    static async getCurrentUser() {
        const token = localStorage.getItem('accessToken');
        if (!token) return null;

        try {
            // 解析 JWT token（仅解析，不验证签名）
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(window.atob(base64));
            
            // 只返回必要的用户信息
            return {
                id: payload.sub,
                username: payload.username,
                role: payload.role
            };
        } catch (error) {
            console.error('Error parsing token:', error);
            return null;
        }
    }

    // 检查用户是否有权限访问当前页面
    static async checkPageAccess() {
        const currentPath = window.location.pathname;
        const user = await this.getCurrentUser();

        // 未登录用户处理
        if (!user) {
            if (!unauthorizedRoutes.includes(currentPath)) {
                window.location.href = '/pages/login.html';
                return false;
            }
            return true;
        }

        // 已登录用户处理
        if (unauthorizedRoutes.includes(currentPath)) {
            window.location.href = '/pages/dashboard.html';
            return false;
        }

        // 检查用户角色权限
        const userRoutes = routePermissions[user.role] || [];
        const hasPermission = userRoutes.some(route => 
            currentPath.startsWith(route) || authorizedRoutes.includes(currentPath)
        );

        if (!hasPermission) {
            window.location.href = '/pages/dashboard.html';
            return false;
        }

        return true;
    }

    // 页面加载时执行权限检查
    static async initPageAuth() {
        try {
            const hasAccess = await this.checkPageAccess();
            if (!hasAccess) return false;

            const user = await this.getCurrentUser();
            return { user, hasAccess };
        } catch (error) {
            console.error('Auth check error:', error);
            return { user: null, hasAccess: false };
        }
    }
}

// 导出权限检查类
export default AuthService;

// Token处理函数
async function refreshToken() {
    try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch('http://localhost:5000/api/refresh', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });

        const data = await response.json();
        if (data.success) {
            localStorage.setItem('accessToken', data.access_token);
            return data.access_token;
        } else {
            throw new Error('Token refresh failed');
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        // 清除所有token并重定向到登录页
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/pages/login.html';
        throw error;
    }
}

// API请求拦截器
async function fetchWithAuth(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    
    if (!token) {
        throw new Error('No access token available');
    }

    // 添加token到请求头
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    try {
        const response = await fetch(url, { ...options, headers });
        
        if (response.status === 401) {
            // Token过期，尝试刷新
            token = await refreshToken();
            headers.Authorization = `Bearer ${token}`;
            return fetch(url, { ...options, headers });
        }
        
        return response;
    } catch (error) {
        console.error('Request error:', error);
        throw error;
    }
}

