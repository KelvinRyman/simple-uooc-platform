async function logout() {
    try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            window.location.href = '/pages/login.html';
            return;
        }

        // 从token中解析用户信息
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        
        // 根据用户角色选择登出API
        const logoutEndpoint = payload.role === 'guest' 
            ? 'http://localhost:5000/api/guest/logout'
            : 'http://localhost:5000/api/logout';

        const response = await fetch(logoutEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            // 清除所有本地存储的信息
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('rememberedUsername');
            localStorage.removeItem('rememberedPassword');
            
            // 重定向到登录页
            window.location.href = '/pages/login.html';
        } else {
            console.error('登出失败:', data.message);
            alert(data.message);
        }
    } catch (error) {
        console.error('登出错误:', error);
        alert('登出失败，请重试');
    }
}
