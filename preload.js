const { contextBridge, ipcRenderer } = require('electron');
const path = require('path');
const fs = require('fs');

// Expor APIs seguras para o processo de renderização
contextBridge.exposeInMainWorld('electronAPI', {
  // File System APIs
  fileSystem: {
    saveAudioFile: async (fileName, audioData) => {
      return await ipcRenderer.invoke('save-audio-file', { fileName, audioData });
    },
    readAudioFile: async (filePath) => {
      return await ipcRenderer.invoke('read-audio-file', filePath);
    },
    getRecordingsPath: async () => {
      return await ipcRenderer.invoke('get-recordings-path');
    },
    listRecordings: async () => {
      return await ipcRenderer.invoke('list-recordings');
    },
    deleteRecording: async (fileName) => {
      return await ipcRenderer.invoke('delete-recording', fileName);
    }
  },
  
  // General File APIs for fileManager
  createDirectory: async (dirPath) => {
    return await ipcRenderer.invoke('create-directory', dirPath);
  },
  saveFile: async (filePath, content) => {
    return await ipcRenderer.invoke('save-file', { filePath, content });
  },
  readFile: async (filePath) => {
    return await ipcRenderer.invoke('read-file', filePath);
  },
  deleteFile: async (filePath) => {
    return await ipcRenderer.invoke('delete-file', filePath);
  },
  listFiles: async (dirPath) => {
    return await ipcRenderer.invoke('list-files', dirPath);
  },

  // Transcription APIs
  transcription: {
    transcribeAudio: async (audioData, options) => {
      return await ipcRenderer.invoke('transcribe-audio', { audioData, options });
    },
    saveTranscription: async (fileName, transcriptionData) => {
      return await ipcRenderer.invoke('save-transcription', { fileName, transcriptionData });
    },
    getTranscription: async (fileName) => {
      return await ipcRenderer.invoke('get-transcription', fileName);
    }
  },

  // Application APIs
  app: {
    getVersion: () => ipcRenderer.invoke('app-version'),
    quit: () => ipcRenderer.send('app-quit'),
    minimize: () => ipcRenderer.send('window-minimize'),
    openExternal: (url) => ipcRenderer.invoke('open-external', url)
  },

  // Settings APIs
  settings: {
    get: async (key) => {
      return await ipcRenderer.invoke('settings-get', key);
    },
    set: async (key, value) => {
      return await ipcRenderer.invoke('settings-set', { key, value });
    },
    getAll: async () => {
      return await ipcRenderer.invoke('settings-get-all');
    }
  },

  // Dialog APIs
  dialog: {
    showError: (title, content) => {
      return ipcRenderer.invoke('show-error-dialog', { title, content });
    },
    showInfo: (title, content) => {
      return ipcRenderer.invoke('show-info-dialog', { title, content });
    },
    showOpenDialog: (options) => {
      return ipcRenderer.invoke('show-open-dialog', options);
    },
    showSaveDialog: (options) => {
      return ipcRenderer.invoke('show-save-dialog', options);
    }
  },

  // Audio APIs
  audio: {
    getDevices: async () => {
      return await ipcRenderer.invoke('get-audio-devices');
    },
    setDevice: async (deviceId) => {
      return await ipcRenderer.invoke('set-audio-device', deviceId);
    }
  },

  // Event listeners
  on: (channel, callback) => {
    const validChannels = [
      'transcription-progress',
      'transcription-complete',
      'transcription-error',
      'recording-saved',
      'settings-changed'
    ];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, ...args) => callback(...args));
    }
  },

  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});