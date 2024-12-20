import AuthService from './auth.js';

// 初始化仪表盘页面
async function initDashboard() {
    try {
        const { user, hasAccess } = await AuthService.initPageAuth();
        
        if (hasAccess && user) {
            updateUserInfo(user);
            updateNavigation(user.role);
        }
    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

// 更新用户信息显示
function updateUserInfo(user) {
    const usernameElement = document.getElementById('username');
    if (usernameElement) {
        usernameElement.textContent = user.username;
    }
    
    // 更新头像（如果用户有自定义头像）
    const avatarElement = document.querySelector('.avatar');
    if (avatarElement && user.avatar) {
        avatarElement.src = user.avatar;
    }
}

// 根据用户角色更新导航菜单
function updateNavigation(role) {
    const navLinks = document.querySelector('.nav-links');
    
    // 根据角色隐藏/显示特定链接
    const links = navLinks.getElementsByTagName('a');
    for (let link of links) {
        switch (role) {
            case 'student':
                if (link.href.includes('users.html') || link.href.includes('logs.html')) {
                    link.style.display = 'none';
                }
                break;
            case 'teacher':
                if (link.href.includes('logs.html')) {
                    link.style.display = 'none';
                }
                break;
            case 'guest':
                if (!link.href.includes('activities.html')) {
                    link.style.display = 'none';
                }
                break;
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initDashboard);
