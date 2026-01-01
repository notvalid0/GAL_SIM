const { spawn } = require('child_process');
const path = require('path');

// 获取系统代理设置
const proxy = process.env.HTTPS_PROXY || process.env.https_proxy || process.env.HTTP_PROXY || process.env.http_proxy;

if (!proxy) {
  console.log('⚠️  未检测到系统代理设置');
  console.log('💡 如果您使用透明代理，请确保网络连接正常');
} else {
  console.log(`🔗 检测到代理设置: ${proxy}`);
}

console.log('🚀 开始构建 Windows 版本 (带代理支持)...');

// 设置环境变量
const env = {
  ...process.env,
  ELECTRON_BUILDER_HTTPS_PROXY: proxy,
  ELECTRON_BUILDER_HTTP_PROXY: proxy,
};

// 运行 electron-builder
const buildProcess = spawn('npx', ['electron-builder', '--win'], {
  cwd: process.cwd(),
  env: env,
  stdio: 'inherit'
});

buildProcess.on('close', (code) => {
  if (code === 0) {
    console.log('✅ 构建成功完成!');
  } else {
    console.log(`❌ 构建失败，退出码: ${code}`);
    process.exit(code);
  }
});

buildProcess.on('error', (error) => {
  console.error('❌ 构建过程出错:', error.message);
  process.exit(1);
});