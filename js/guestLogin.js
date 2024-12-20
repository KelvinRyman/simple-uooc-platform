async function guestLogin() {
    const errorMessage = document.getElementById('error-message');
    const loadingText = document.createElement('span');
    loadingText.textContent = '正在创建游客账号...';
    
    try {
        errorMessage.textContent = '';
        errorMessage.appendChild(loadingText);
        
        const response = await fetch('http://localhost:5000/api/guest/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            // 保存JWT tokens
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            
            // 重定向到游客仪表盘
            window.location.href = '/pages/dashboard.html';
        } else {
            errorMessage.textContent = data.message || '游客登录失败';
        }
    } catch (error) {
        errorMessage.textContent = '服务器连接错误，请稍后重试';
        console.error('Error:', error);
    }
}
