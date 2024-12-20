document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const usernameInput = document.getElementById('username');
    const rememberUsername = document.getElementById('remember-username');
    const rememberPassword = document.getElementById('remember-password');

    // 从localStorage加载保存的用户名和密码
    const savedUsername = localStorage.getItem('rememberedUsername');
    const savedPassword = localStorage.getItem('rememberedPassword');
    
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberUsername.checked = true;
    }
    
    if (savedPassword) {
        passwordInput.value = savedPassword;
        rememberPassword.checked = true;
    }

    // 切换密码显示/隐藏
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        togglePassword.textContent = type === 'password' ? '👁‍🗨' : '👁‍🗨';
    });

    // 从 localStorage 获取登录失败次数
    let loginFailCount = parseInt(localStorage.getItem('loginFailCount') || '0');
    if (loginFailCount >= 3) {
        document.getElementById('recaptcha-container').style.display = 'block';
    }
});

async function submitForm(event) {
    event.preventDefault();
    
    const form = document.getElementById('login_form');
    const errorMessage = document.getElementById('error-message');
    const recaptchaContainer = document.getElementById('recaptcha-container');
    
    let loginFailCount = parseInt(localStorage.getItem('loginFailCount') || '0');
    
    // 如果失败次数>=3，检查验证码
    if (loginFailCount >= 3) {
        const recaptchaResponse = grecaptcha.getResponse();
        if (!recaptchaResponse) {
            errorMessage.textContent = '请完成人机验证';
            return;
        }
    }

    const username = form.username.value;
    const password = form.password.value;
    
    // 保存用户名和密码
    if (document.getElementById('remember-username').checked) {
        localStorage.setItem('rememberedUsername', username);
    } else {
        localStorage.removeItem('rememberedUsername');
    }
    
    if (document.getElementById('remember-password').checked) {
        localStorage.setItem('rememberedPassword', password);
    } else {
        localStorage.removeItem('rememberedPassword');
    }

    const formData = {
        userType: form.userType.value,
        username: form.username.value.trim(),
        password: form.password.value,
        recaptchaToken: loginFailCount >= 3 ? grecaptcha.getResponse() : null
    };

    if (!formData.username || !formData.password) {
        errorMessage.textContent = '请输入用户名和密码';
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // 存储Token
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            
            // 保存用户信息
            if (document.getElementById('remember-username').checked) {
                localStorage.setItem('rememberedUsername', formData.username);
            }
            
            if (document.getElementById('remember-password').checked) {
                localStorage.setItem('rememberedPassword', formData.password);
            }

            // 重置登录失败次数
            localStorage.setItem('loginFailCount', '0');

            // 根据角色重定向
            switch (data.user.role) {
                case 'student':
                    window.location.href = '/pages/dashboard.html';
                    break;
                case 'teacher':
                    window.location.href = '/pages/teacher/dashboard.html';
                    break;
                case 'admin':
                    window.location.href = '/pages/admin/dashboard.html';
                    break;
            }
        } else {
            // 登录失败，增加失败次数
            loginFailCount++;
            localStorage.setItem('loginFailCount', loginFailCount.toString());
            
            // 如果达到3次，显示验证码
            if (loginFailCount >= 3) {
                recaptchaContainer.style.display = 'block';
                grecaptcha.reset();
            }
            
            errorMessage.textContent = data.message;
        }
    } catch (error) {
        errorMessage.textContent = '服务器连接错误，请稍后重试';
        console.error('Error:', error);
    }
}
