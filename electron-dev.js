const { spawn } = require('child_process');
const electron = require('electron');
const path = require('path');

// Start Vite dev server
console.log('Starting Vite dev server...');
const vite = spawn('npm', ['run', 'dev'], {
  shell: true,
  stdio: 'inherit'
});

// Wait for Vite to start, then launch Electron
setTimeout(() => {
  console.log('Starting Electron...');
  
  const electronProcess = spawn(electron, ['.'], {
    stdio: 'inherit',
    env: {
      ...process.env,
      NODE_ENV: 'development'
    }
  });

  electronProcess.on('close', () => {
    vite.kill();
    process.exit(0);
  });
}, 3000);

// Handle process termination
process.on('SIGINT', () => {
  vite.kill();
  process.exit(0);
});