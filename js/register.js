document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('register_form');
    const errorMsg = document.getElementById('errormsg');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const formData = {
            username: document.getElementById('accountnumber').value,
            password: document.getElementById('password').value,
            role: document.getElementById('userType').value,
            email: document.getElementById('email').value || null
        };

        // 密码确认验证
        const rePassword = document.getElementById('re_password').value;
        if (formData.password !== rePassword) {
            errorMsg.textContent = '两次输入的密码不一致';
            return;
        }

        // 隐私政策确认
        if (!document.getElementById('privacy').checked) {
            errorMsg.textContent = '请阅读并同意隐私政策';
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                // 注册成功，重定向到登录页
                window.location.href = 'login.html';
            } else {
                // 显示错误信息
                errorMsg.textContent = data.message || '注册失败，请稍后重试';
            }
        } catch (error) {
            console.error('Registration error:', error);
            errorMsg.textContent = '注册失败，请检查网络连接';
        }
    });

    // 实时密码匹配验证
    const password = document.getElementById('password');
    const rePassword = document.getElementById('re_password');
    
    function validatePassword() {
        if (password.value !== rePassword.value) {
            rePassword.setCustomValidity('密码不匹配');
        } else {
            rePassword.setCustomValidity('');
        }
    }

    password.addEventListener('change', validatePassword);
    rePassword.addEventListener('keyup', validatePassword);
});
