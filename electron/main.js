const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const dotenv = require('dotenv');

let mainWindow;
let pythonProcess;
let serverReady = false;

// 检查并确保环境变量文件存在
function checkEnvFile() {
  const resourcesPath = isDev 
    ? path.join(__dirname, '..') 
    : process.resourcesPath;
  
  const envPath = isDev
    ? path.join(__dirname, '../.env')
    : path.join(resourcesPath, 'app/.env');
  
  const envExamplePath = isDev
    ? path.join(__dirname, '../.env.example')
    : path.join(resourcesPath, 'app/.env.example');
  
  // 检查是否存在.env文件
  if (!fs.existsSync(envPath)) {
    console.warn('⚠️ .env文件不存在，正在检查是否为首次运行...');
    
    // 如果是生产环境，尝试从.env.example创建默认的.env文件
    if (!isDev && fs.existsSync(envExamplePath)) {
      try {
        const envExampleContent = fs.readFileSync(envExamplePath, 'utf8');
        // 创建新的.env文件，但保留用户可能已有的配置
        if (!fs.existsSync(envPath)) {
          fs.writeFileSync(envPath, envExampleContent);
          console.log('.env文件已从示例文件创建');
        }
      } catch (err) {
        console.error('创建.env文件时出错:', err);
      }
    }
  }
  
  // 检查API密钥是否已配置
  dotenv.config({ path: envPath });
  const apiKey = process.env.LLM_API_KEY || process.env.OPENAI_API_KEY;
  if (!apiKey || apiKey === 'your_api_key_here') {
    console.warn('⚠️  警告: API密钥未配置或仍为默认值，请在 .env 文件中配置');
    console.warn('   示例: LLM_API_KEY=sk-...');
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../gal_sim/static/favicon.ico') // 使用项目中的favicon作为应用图标
  });

  // 在开发模式下使用本地服务器，生产模式下启动FastAPI服务器
  if (isDev) {
    mainWindow.loadURL('http://localhost:8000');
  } else {
    // 启动FastAPI服务器并等待其就绪
    startFastAPIServer().then(() => {
      mainWindow.loadURL('http://localhost:8000');
    }).catch((err) => {
      console.error('Failed to start FastAPI server:', err);
      mainWindow.loadURL('http://localhost:8000'); // 尝试连接，即使启动失败
    });
  }

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

// 启动FastAPI服务器
function startFastAPIServer() {
  return new Promise((resolve, reject) => {
    // 检查环境配置
    checkEnvFile();
    
    const resourcesPath = isDev 
      ? path.join(__dirname, '..') 
      : process.resourcesPath;
    
    const appPath = isDev
      ? path.join(__dirname, '../run_server.py')
      : path.join(resourcesPath, 'app/run_server.py');
    
    // 根据操作系统确定Python可执行文件路径
    let pythonCmd = 'python3';
    
    if (process.platform === 'win32') {
      pythonCmd = 'python';
    }
    
    // 检查是否在Electron打包后的环境中
    const isPackaged = app.isPackaged;
    
    // Windows环境下尝试多种Python执行文件名
    if (process.platform === 'win32') {
      // 检查是否有python.exe
      const { execSync } = require('child_process');
      try {
        execSync('python --version');
        pythonCmd = 'python';
      } catch (e) {
        try {
          execSync('python.exe --version');
          pythonCmd = 'python.exe';
        } catch (e) {
          console.warn('⚠️ 未找到Python命令，应用可能无法正常工作');
          pythonCmd = 'python'; // 默认回退
        }
      }
    }
    
    const workingDir = isDev
      ? path.join(__dirname, '..')
      : path.join(resourcesPath, 'app');
    
    // 在Windows环境下，可能需要使用完整的Python路径或添加额外的环境变量
    const spawnOptions = {
      cwd: workingDir,
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1'
      }
    };
    
    // 在Windows上设置适当的PATH
    if (process.platform === 'win32') {
      spawnOptions.env.PATH = process.env.PATH || '';
      
      // 在Windows上，可能需要添加Python安装路径到环境变量
      const pythonPaths = [
        'C:\\Python39\\Scripts\\',
        'C:\\Python38\\Scripts\\',
        'C:\\Python37\\Scripts\\',
        'C:\\Python39\\',
        'C:\\Python38\\',
        'C:\\Python37\\'
      ];
      
      for (const pythonPath of pythonPaths) {
        if (spawnOptions.env.PATH.indexOf(pythonPath) === -1) {
          spawnOptions.env.PATH = `${pythonPath};${spawnOptions.env.PATH}`;
        }
      }
    }
    
    console.log('Starting FastAPI server...');
    console.log('Python command:', pythonCmd);
    console.log('App path:', appPath);
    console.log('Working directory:', workingDir);
    console.log('Resources path:', resourcesPath);
    console.log('Is packaged:', app.isPackaged);
    
    pythonProcess = spawn(pythonCmd, [appPath], spawnOptions);

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`FastAPI: ${output}`);
      
      // 检测服务器是否已启动
      if (!serverReady && (output.includes('Uvicorn running on') || output.includes('Application startup complete'))) {
        serverReady = true;
        console.log('FastAPI server is ready');
        resolve();
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`FastAPI Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      console.log(`FastAPI process exited with code ${code}`);
      if (!serverReady) {
        // 在Windows环境下，如果服务器启动失败，尝试使用更具体的错误信息
        if (process.platform === 'win32') {
          console.error('FastAPI server failed to start on Windows. This may be due to:');
          console.error('1. Python is not installed or not in PATH');
          console.error('2. Required Python packages are not installed');
          console.error('3. Port 8000 is already in use');
          console.error('4. Antivirus software blocking the process');
          
          // 尝试打开一个错误提示页面
          if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.loadFile(path.join(__dirname, 'error.html')).catch(() => {
              mainWindow.webContents.loadURL(`data:text/html;charset=utf-8,` + 
                `<h2>无法启动GAL-SIM服务</h2>` +
                `<p>错误代码: ${code}</p>` +
                `<p>可能的原因:</p>` +
                `<ul>` +
                `<li>Python未安装或未添加到PATH</li>` +
                `<li>缺少必要的Python包</li>` +
                `<li>端口8000被占用</li>` +
                `</ul>` +
                `<p>请确保已安装Python 3.7+和项目依赖</p>`);
            });
          }
        }
        reject(new Error(`Server exited with code ${code} before becoming ready`));
      }
    });
    
    // 设置超时，防止无限等待
    setTimeout(() => {
      if (!serverReady) {
        console.warn('⚠️ Server startup timeout after 30 seconds');
        console.warn('   The server may still be starting. If the app does not load,');
        console.warn('   please check that Python and dependencies are properly installed.');
        resolve(); // 超时后仍然继续，而不是失败
      }
    }, 30000); // 30秒超时
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') app.quit();
});

app.on('quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
});