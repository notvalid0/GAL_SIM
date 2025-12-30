const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn, exec } = require('child_process');

let mainWindow;
let pythonProcess;

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
    // 启动FastAPI服务器
    startFastAPIServer();
    mainWindow.loadURL('http://localhost:8000');
  }

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

// 启动FastAPI服务器
function startFastAPIServer() {
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
  
  const workingDir = isDev
    ? path.join(__dirname, '..')
    : path.join(resourcesPath, 'app');
  
  console.log('Starting FastAPI server...');
  console.log('Python command:', pythonCmd);
  console.log('App path:', appPath);
  console.log('Working directory:', workingDir);
  
  pythonProcess = spawn(pythonCmd, [appPath], {
    cwd: workingDir,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1'
    }
  });

  let serverReady = false;

  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`FastAPI: ${output}`);
    
    // 检测服务器是否已启动
    if (output.includes('Uvicorn running on') || output.includes('Application startup complete')) {
      serverReady = true;
      console.log('FastAPI server is ready');
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`FastAPI process exited with code ${code}`);
  });
  
  // 等待服务器启动，使用轮询检查
  const maxWaitTime = 30000; // 最多等待30秒
  const checkInterval = 500; // 每500ms检查一次
  let waitedTime = 0;
  
  const checkServer = setInterval(() => {
    if (serverReady || waitedTime >= maxWaitTime) {
      clearInterval(checkServer);
      if (!serverReady) {
        console.warn('Server may not be ready yet, but proceeding anyway');
      }
    }
    waitedTime += checkInterval;
  }, checkInterval);
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