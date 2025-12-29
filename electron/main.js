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
  // 使用Python虚拟环境运行FastAPI服务器
  const venvPath = path.join(__dirname, '../venv/bin/python');
  const appPath = path.join(__dirname, '../run_server.py');
  
  pythonProcess = spawn(venvPath, [appPath], {
    cwd: path.join(__dirname, '..'),
    env: process.env
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`FastAPI: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`FastAPI process exited with code ${code}`);
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