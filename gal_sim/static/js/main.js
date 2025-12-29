// 全局变量
let currentSessionId = null;
let currentTheme = null;
let currentAffection = 50;

// DOM元素
const themeSelectionDiv = document.getElementById('theme-selection');
const dialogueAreaDiv = document.getElementById('dialogue-area');
const dialogueHistoryDiv = document.getElementById('dialogue-history');
const choicesAreaDiv = document.getElementById('choices-area');
const currentThemeSpan = document.getElementById('current-theme');
const loadingDiv = document.getElementById('loading');
const startBtn = document.getElementById('startBtn');
const customThemeRadio = document.getElementById('customTheme');
const customThemeInputDiv = document.getElementById('customThemeInput');
const customThemeTextInput = document.getElementById('customThemeText');
const affectionDisplay = document.getElementById('affection-display');
const affectionValue = document.getElementById('affection-value');
const affectionFill = document.getElementById('affection-fill');

// 事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 设置背景图片
    setBackgroundImage();
    
    // 主题选择切换
    document.querySelectorAll('input[name="themeOption"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'custom') {
                customThemeInputDiv.style.display = 'block';
            } else {
                customThemeInputDiv.style.display = 'none';
            }
        });
    });
    
    // 开始对话按钮
    startBtn.addEventListener('click', startNewDialogue);
});

// 设置背景图片
async function setBackgroundImage() {
    try {
        // 从图片API获取背景图片
        // 使用fetch来处理可能的重定向
        const imageUrl = 'https://www.loliapi.com/acg/';  // Loliapi ACG图片API
        
        // 使用fetch来检查API响应
        const response = await fetch(imageUrl, { 
            method: 'GET',
            redirect: 'follow'  // 自动跟随重定向
        });
        
        if (response.ok) {
            // 图片API请求成功，直接使用URL设置背景
            document.body.style.backgroundImage = `url('${imageUrl}')`;
            document.body.style.backgroundSize = 'cover';
            document.body.style.backgroundRepeat = 'no-repeat';
            document.body.style.backgroundAttachment = 'fixed';
            document.body.style.backgroundPosition = 'center';
            console.log('背景图片设置成功:', imageUrl);
        } else {
            console.error('API请求失败，状态码:', response.status);
            // 使用默认背景
            document.body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    } catch (error) {
        console.error('设置背景图片失败:', error);
        // 如果发生错误，使用默认背景
        document.body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        
        // 作为备选方案，使用Image对象尝试加载
        try {
            const img = new Image();
            img.onload = function() {
                document.body.style.backgroundImage = `url('https://www.loliapi.com/acg/')`;
                document.body.style.backgroundSize = 'cover';
                document.body.style.backgroundRepeat = 'no-repeat';
                document.body.style.backgroundAttachment = 'fixed';
                document.body.style.backgroundPosition = 'center';
            };
            
            img.onerror = function() {
                document.body.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            };
            
            img.src = 'https://www.loliapi.com/acg/';
        } catch (imgError) {
            console.error('备选方案也失败:', imgError);
        }
    }
}

// 开始新对话
async function startNewDialogue() {
    const themeOption = document.querySelector('input[name="themeOption"]:checked').value;
    let theme = null;
    let customTheme = null;
    
    if (themeOption === 'auto') {
        theme = 'auto';
    } else if (themeOption === 'custom') {
        customTheme = customThemeTextInput.value.trim();
        if (!customTheme) {
            alert('请输入自定义主题');
            return;
        }
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/v1/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                theme: theme,
                custom_theme: customTheme
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentSessionId = data.session_id;
        currentTheme = data.theme;
        currentAffection = data.affection;
        
        // 更新好感度显示
        updateAffectionDisplay(currentAffection);
        affectionDisplay.style.display = 'block';
        
        // 更新UI
        currentThemeSpan.textContent = currentTheme;
        dialogueAreaDiv.style.display = 'block';
        themeSelectionDiv.style.display = 'none';
        
        // 显示初始对话
        addMessageToHistory('character', data.initial_dialogue);
        
        // 显示选项
        displayChoices(data.choices);
        
    } catch (error) {
        console.error('开始对话失败:', error);
        alert('开始对话失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// 继续对话
async function continueDialogue(userChoice) {
    if (!currentSessionId) {
        alert('会话未开始，请先开始对话');
        return;
    }
    
    // 添加用户选择到历史记录
    addMessageToHistory('user', userChoice);
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/v1/dialogue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: userChoice,
                session_id: currentSessionId,
                theme: currentTheme
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 更新好感度
        currentAffection = data.affection;
        updateAffectionDisplay(currentAffection);
        
        // 显示角色回应
        addMessageToHistory('character', data.character_response);
        
        // 显示新选项
        displayChoices(data.choices);
        
    } catch (error) {
        console.error('继续对话失败:', error);
        alert('继续对话失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// 添加消息到历史记录
function addMessageToHistory(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${role === 'user' ? 'user-message' : 'character-message'}`;
    
    messageDiv.textContent = content;
    dialogueHistoryDiv.appendChild(messageDiv);
    
    // 滚动到底部
    dialogueHistoryDiv.scrollTop = dialogueHistoryDiv.scrollHeight;
}

// 显示选项
function displayChoices(choices) {
    choicesAreaDiv.innerHTML = '';
    
    if (!choices || choices.length === 0) {
        const noChoicesDiv = document.createElement('div');
        noChoicesDiv.className = 'alert alert-info';
        noChoicesDiv.textContent = '没有可用的选项，请重新开始对话。';
        choicesAreaDiv.appendChild(noChoicesDiv);
        return;
    }
    
    // 确保有4个选项
    while (choices.length < 4) {
        choices.push('');
    }
    
    choices.forEach((choice, index) => {
        if (!choice) return; // 跳过空选项
        
        const choiceBtn = document.createElement('button');
        choiceBtn.className = 'choice-btn btn';
        choiceBtn.type = 'button';
        
        const letter = String.fromCharCode(65 + index); // A, B, C, D
        choiceBtn.innerHTML = `
            <span class="choice-letter">${letter}</span>
            ${choice}
        `;
        
        choiceBtn.addEventListener('click', () => continueDialogue(choice));
        choicesAreaDiv.appendChild(choiceBtn);
    });
}

// 显示/隐藏加载指示器
function showLoading(show) {
    if (show) {
        loadingDiv.style.display = 'block';
        // 禁用选项按钮
        document.querySelectorAll('.choice-btn').forEach(btn => {
            btn.disabled = true;
        });
    } else {
        loadingDiv.style.display = 'none';
        // 启用选项按钮
        document.querySelectorAll('.choice-btn').forEach(btn => {
            btn.disabled = false;
        });
    }
}

// 更新好感度显示
function updateAffectionDisplay(affection) {
    // 更新数值显示
    affectionValue.textContent = affection;
    
    // 更新进度条
    const percentage = Math.max(0, Math.min(100, affection)); // 确保在0-100范围内
    affectionFill.style.width = `${percentage}%`;
    
    // 根据好感度值改变颜色
    if (affection < 20) {
        affectionFill.style.background = 'linear-gradient(90deg, #ff6b6b, #ffa5a5)'; // 红色
    } else if (affection < 40) {
        affectionFill.style.background = 'linear-gradient(90deg, #ffa5a5, #ffd700)'; // 橙色
    } else if (affection < 60) {
        affectionFill.style.background = 'linear-gradient(90deg, #ffd700, #98fb98)'; // 黄色
    } else if (affection < 80) {
        affectionFill.style.background = 'linear-gradient(90deg, #98fb98, #87ceeb)'; // 绿色
    } else {
        affectionFill.style.background = 'linear-gradient(90deg, #87ceeb, #4ecdc4)'; // 蓝色/青色
    }
}