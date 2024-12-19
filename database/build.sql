-- 要動的表: 
-- 课程进行注册 = course_enrollments + users + courses

-- 在线学习 = users + courses + course_contents + learning_progress
-- 完成测练 = quiz_questions + learning_progress
-- 查看课程的学习任务 = course_enrollments + assignments + learning_progress

-- 课程讨论 = discussions
-- 课程的笔记功能 = notes

-- 教师查看学生作业提交情况 = users + course_enrollments + assignment_submissions
-- 提交作业 = assignments + assignment_submissions
-- 查看已完成作业及评测结果 = assignment_submissions




-- 系统支持的扩展功能
-- 课程置顶功能:
-- 表：pinned_courses。
-- 描述：可将某些课程置顶以提升展示优先级。

-- 登录状态管理:
-- 表：login_attempts, account_status。
-- 描述：管理用户的登录尝试记录及账号锁定状态。
-- 

-- 用户表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role ENUM('student', 'teacher', 'admin', 'guest') NOT NULL,
    avatar VARCHAR(255),
    signature TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1 COMMENT '1:正常 0:禁用'
);

-- 课程表
CREATE TABLE courses (
    id int primary key AUTO_INCREMENT, 
    title VARCHAR(100) NOT NULL,
    description TEXT,
    cover_image VARCHAR(255),
    teacher_id VARCHAR(36) NOT NULL,
    category VARCHAR(50),
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    likes INT DEFAULT 0,
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- 课程内容表
CREATE TABLE course_contents (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    title VARCHAR(100) NOT NULL,
    type ENUM('document', 'video', 'audio', 'image') NOT NULL,
    content_url VARCHAR(255),
    sort_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 置顶课程表
CREATE TABLE pinned_courses (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    sort_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 课程注册表
CREATE TABLE course_enrollments (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    status ENUM('active', 'completed', 'dropped') DEFAULT 'active',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 作业表
CREATE TABLE assignments (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 作业提交表
CREATE TABLE assignment_submissions (
    id VARCHAR(36) PRIMARY KEY,
    assignment_id VARCHAR(36) NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    content TEXT,
    file_url VARCHAR(255),
    score DECIMAL(5,2),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 讨论表
CREATE TABLE discussions (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    content TEXT,
    parent_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 学习笔记表
CREATE TABLE notes (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- 测试题库表
CREATE TABLE quiz_questions (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(36) NOT NULL,
    creator_id VARCHAR(36) NOT NULL,
    type ENUM('single', 'multiple', 'judge', 'fill', 'essay') NOT NULL,
    question TEXT NOT NULL,
    options JSON,
    answer TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

-- 学习进度表
CREATE TABLE learning_progress (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(36) NOT NULL,
    content_id VARCHAR(36) NOT NULL,
    progress DECIMAL(5,2) DEFAULT 0,
    last_position INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (content_id) REFERENCES course_contents(id)
);

-- 登录失败记录表
CREATE TABLE login_attempts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    ip_address VARCHAR(45),
    device_id VARCHAR(255),
    mac_address VARCHAR(17),
    attempt_time DATETIME,
    is_successful BOOLEAN,
    INDEX(user_id, attempt_time)
);

-- 账号状态表
CREATE TABLE account_status (
    user_id INT PRIMARY KEY,
    is_locked BOOLEAN DEFAULT FALSE,
    lock_reason VARCHAR(100),
    lock_time DATETIME,
    unlock_time DATETIME,
    failed_attempts INT DEFAULT 0
);

-- 索引
CREATE INDEX idx_course_category ON courses(category);
CREATE INDEX idx_course_status ON courses(status);
CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_learning_progress ON learning_progress(student_id, content_id);
