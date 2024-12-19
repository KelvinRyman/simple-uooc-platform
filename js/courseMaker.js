document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register_form");
    const registerButton = registerForm.querySelector(".register_button");
    const errorMsg = document.getElementById("errormsg");

    // 啟用提交按鈕檢查
    registerForm.addEventListener("input", function () {
        const courseName = registerForm.coursename.value.trim();
        const teacherID= registerForm.teacherid.value.trim();

        if (courseName && teacherID ) {
            registerButton.disabled = false;
        } else {
            registerButton.disabled = true;
        }
    });

    // 提交表單
    registerForm.onsubmit = async function (event) {
        event.preventDefault(); // 防止默認刷新頁面

        const courseName = registerForm.coursename.value.trim();
        const teacherID= registerForm.teacherid.value.trim();

        try {
            const response = await fetch('http://localhost:5000/api/course', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: courseName, teacher_id: teacherID }),
            });

            if (response.ok) {
                const data = await response.json();
                alert("建立成功！課程ID：" + data.id);
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
