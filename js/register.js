document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register_form");
    const registerButton = registerForm.querySelector(".register_button");
    const errorMsg = document.getElementById("errormsg");

    // 啟用提交按鈕檢查
    registerForm.addEventListener("input", function () {
        const account = registerForm.accountnumber.value.trim();
        const password = registerForm.password.value.trim();
        const rePassword = registerForm.re_password.value.trim();

        if (account && password && password === rePassword) {
            registerButton.disabled = false;
            errorMsg.textContent = "";
        } else {
            registerButton.disabled = true;
            errorMsg.textContent = password !== rePassword ? "两次密码不一致" : "";
        }
    });

    // 提交表單
    registerForm.onsubmit = async function (event) {
        event.preventDefault(); // 防止默認刷新頁面

        const account = registerForm.accountnumber.value.trim();
        const password = registerForm.password.value.trim();

        try {
            const response = await fetch('http://localhost:5000/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: account, password: password }),
            });

            if (response.ok) {
                const data = await response.json();
                alert("注册成功！用户 ID：" + data.user_id);
                window.location.href = "./student.html"; // 跳轉到登錄頁面
            } else {
                const errorData = await response.json();
                errorMsg.textContent = errorData.message || "注册失败，请重试";
            }
        } catch (err) {
            console.error(err);
            errorMsg.textContent = "服务器错误，请稍后再试";
        }
    };
});
