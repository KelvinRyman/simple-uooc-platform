document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("register_form");
    const registerButton = registerForm.querySelector(".register_button");
    const errorMsg = document.getElementById("errormsg");
    // 提交表單
    registerForm.onsubmit = async function (event) {
        event.preventDefault(); // 防止默認刷新頁面

        //const courseregisterID = registerForm.courseregisterid.value.trim();
        const courseID = registerForm.courseid.value.trim();
        const studentID= registerForm.studentid.value.trim();

        try {
            const response = await fetch('http://localhost:5000/api/course/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                //body: JSON.stringify({ id: courseID, title: courseName, teacher_id: teacherID }),
                body: JSON.stringify({ course_id: courseID , student_id: studentID}),
            });

            if (response.ok) {
                const data = await response.json();
                alert("注冊課程成功！注冊課程 ID：" + data.id);
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
