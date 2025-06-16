const { app, BrowserWindow, ipcMain, dialog, Menu, protocol } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const { shell } = require('electron');

// Habilitar live reload apenas em desenvolvimento
if (process.env.NODE_ENV === 'development') {
  require('electron-reload')(__dirname, {
    electron: path.join(__dirname, 'node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
  });
}

let mainWindow;

function createWindow() {
  // Criar a janela do navegador
  mainWindow = new BrowserWindow({
    width: 320,
    height: 240,
    resizable: false, // Desabilita redimensionamento
    maximizable: false, // Desabilita maximização
    fullscreenable: false, // Desabilita tela cheia
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, // Isolamento de contexto para segurança
      nodeIntegration: false // Desabilita Node.js no renderer por segurança
    }
  });

  // Em desenvolvimento, carrega do servidor Vite
  const isDev = process.env.NODE_ENV === 'development' || process.env.ELECTRON_DEV === 'true';
  
  if (isDev && !app.isPackaged) {
    mainWindow.loadURL('http://localhost:5173');
    // Abrir DevTools em desenvolvimento
    mainWindow.webContents.openDevTools();
  } else {
    // Em produção, carrega o arquivo construído
    mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
  }

  // Emitido quando a janela é fechada
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Configurações de segurança para produção
if (!app.isPackaged) {
  // Apenas em desenvolvimento
  app.commandLine.appendSwitch('disable-features', 'OutOfBlinkCors');
}

// Definir protocolo customizado antes do app estar pronto
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
]);

// Este método será chamado quando o Electron terminar de inicializar
app.whenReady().then(() => {
  // Criar menu da aplicação
  const template = [
    {
      label: 'Arquivo',
      submenu: [
        { label: 'Nova Gravação', accelerator: 'CmdOrCtrl+N', click: () => mainWindow.webContents.send('new-recording') },
        { type: 'separator' },
        { label: 'Sair', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: 'Editar',
      submenu: [
        { role: 'undo', label: 'Desfazer' },
        { role: 'redo', label: 'Refazer' },
        { type: 'separator' },
        { role: 'cut', label: 'Recortar' },
        { role: 'copy', label: 'Copiar' },
        { role: 'paste', label: 'Colar' }
      ]
    },
    {
      label: 'Visualizar',
      submenu: [
        { role: 'reload', label: 'Recarregar' },
        { role: 'toggleDevTools', label: 'Ferramentas do Desenvolvedor' },
        { type: 'separator' },
        { role: 'zoomIn', label: 'Aumentar Zoom' },
        { role: 'zoomOut', label: 'Diminuir Zoom' },
        { role: 'resetZoom', label: 'Resetar Zoom' }
      ]
    },
    {
      label: 'Ajuda',
      submenu: [
        { label: 'Sobre', click: () => {
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Sobre Audio Transcription',
            message: 'Audio Transcription App',
            detail: 'Versão 1.0.0\n\nAplicativo para gravação e transcrição de áudio.',
            buttons: ['OK']
          });
        }}
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  createWindow();

  app.on('activate', () => {
    // No macOS, recria a janela quando o ícone do dock é clicado
    if (mainWindow === null) {
      createWindow();
    }
  });
});

// Sair quando todas as janelas forem fechadas
app.on('window-all-closed', () => {
  // No macOS, aplicativos permanecem ativos até serem explicitamente fechados
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Get recordings directory
function getRecordingsDir() {
  const userDataPath = app.getPath('userData');
  return path.join(userDataPath, 'recordings');
}

// Ensure recordings directory exists
async function ensureRecordingsDir() {
  const dir = getRecordingsDir();
  try {
    await fs.mkdir(dir, { recursive: true });
  } catch (error) {
    console.error('Error creating recordings directory:', error);
  }
}

// Initialize app
app.whenReady().then(() => {
  ensureRecordingsDir();
});

// IPC Handlers

// File System handlers
ipcMain.handle('save-audio-file', async (event, { fileName, audioData }) => {
  try {
    const recordingsDir = getRecordingsDir();
    const filePath = path.join(recordingsDir, fileName);
    
    // Convert base64 to buffer if needed
    const buffer = Buffer.from(audioData.split(',')[1] || audioData, 'base64');
    await fs.writeFile(filePath, buffer);
    
    return { success: true, filePath };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('read-audio-file', async (event, filePath) => {
  try {
    const data = await fs.readFile(filePath);
    return { success: true, data: data.toString('base64') };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-recordings-path', async () => {
  return getRecordingsDir();
});

ipcMain.handle('list-recordings', async () => {
  try {
    const recordingsDir = getRecordingsDir();
    const files = await fs.readdir(recordingsDir);
    const recordings = [];
    
    for (const file of files) {
      const filePath = path.join(recordingsDir, file);
      const stats = await fs.stat(filePath);
      recordings.push({
        name: file,
        path: filePath,
        size: stats.size,
        created: stats.birthtime,
        modified: stats.mtime
      });
    }
    
    return { success: true, recordings };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('delete-recording', async (event, fileName) => {
  try {
    const recordingsDir = getRecordingsDir();
    const filePath = path.join(recordingsDir, fileName);
    await fs.unlink(filePath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Transcription handlers
ipcMain.handle('save-transcription', async (event, { fileName, transcriptionData }) => {
  try {
    const recordingsDir = getRecordingsDir();
    const filePath = path.join(recordingsDir, fileName.replace(/\.\w+$/, '.json'));
    await fs.writeFile(filePath, JSON.stringify(transcriptionData, null, 2));
    return { success: true, filePath };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-transcription', async (event, fileName) => {
  try {
    const recordingsDir = getRecordingsDir();
    const filePath = path.join(recordingsDir, fileName.replace(/\.\w+$/, '.json'));
    const data = await fs.readFile(filePath, 'utf-8');
    return { success: true, data: JSON.parse(data) };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// App handlers
ipcMain.handle('app-version', () => {
  return app.getVersion();
});

ipcMain.on('app-quit', () => {
  app.quit();
});

ipcMain.on('window-minimize', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.handle('open-external', async (event, url) => {
  await shell.openExternal(url);
});

// Settings handlers (using simple JSON file)
const settingsPath = path.join(app.getPath('userData'), 'settings.json');

ipcMain.handle('settings-get', async (event, key) => {
  try {
    const data = await fs.readFile(settingsPath, 'utf-8');
    const settings = JSON.parse(data);
    return settings[key];
  } catch (error) {
    return null;
  }
});

ipcMain.handle('settings-set', async (event, { key, value }) => {
  try {
    let settings = {};
    try {
      const data = await fs.readFile(settingsPath, 'utf-8');
      settings = JSON.parse(data);
    } catch (error) {
      // File doesn't exist yet
    }
    
    settings[key] = value;
    await fs.writeFile(settingsPath, JSON.stringify(settings, null, 2));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('settings-get-all', async () => {
  try {
    const data = await fs.readFile(settingsPath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return {};
  }
});

// Dialog handlers
ipcMain.handle('show-error-dialog', async (event, { title, content }) => {
  dialog.showErrorBox(title, content);
});

ipcMain.handle('show-info-dialog', async (event, { title, content }) => {
  const result = await dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: title,
    message: content,
    buttons: ['OK']
  });
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

// Audio device handlers
ipcMain.handle('get-audio-devices', async () => {
  // This would need implementation based on your audio handling library
  return { success: true, devices: [] };
});

ipcMain.handle('set-audio-device', async (event, deviceId) => {
  // This would need implementation based on your audio handling library
  return { success: true };
});

// General file management handlers for fileManager
ipcMain.handle('create-directory', async (event, dirPath) => {
  try {
    const fullPath = path.join(app.getPath('userData'), dirPath);
    await fs.mkdir(fullPath, { recursive: true });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('save-file', async (event, { filePath, content }) => {
  try {
    const fullPath = path.join(app.getPath('userData'), filePath);
    await fs.writeFile(fullPath, content, 'utf-8');
    return { success: true, fullPath };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const fullPath = path.join(app.getPath('userData'), filePath);
    const content = await fs.readFile(fullPath, 'utf-8');
    return { success: true, content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('delete-file', async (event, filePath) => {
  try {
    const fullPath = path.join(app.getPath('userData'), filePath);
    await fs.unlink(fullPath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('list-files', async (event, dirPath) => {
  try {
    const fullPath = path.join(app.getPath('userData'), dirPath);
    const files = await fs.readdir(fullPath);
    return { success: true, files };
  } catch (error) {
    return { success: false, error: error.message, files: [] };
  }
});