const CONVERSATIONS_KEY = 'codemind.conversations.v1'
const SETTINGS_KEY = 'codemind.settings.v1'
const PROJECTS_KEY = 'codemind.projects.v1'

export const defaultSettings = {
  appearance: 'dark',
  compactMode: false,
  showTimestamps: true,
  showLineNumbers: true,
  enterToSend: true,
  streamingAnimation: true,
  explainWhileCoding: false,
  explanationStyle: 'brief',
}

export function readStoredValue(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch (error) {
    console.error(`Could not read CodeMind local setting "${key}".`, error)
    return fallback
  }
}

function scopedKey(key, accountId) {
  return accountId ? `${key}.${accountId}` : key
}

export function readConversations(accountId) {
  const conversations = readStoredValue(scopedKey(CONVERSATIONS_KEY, accountId), null)
  return Array.isArray(conversations)
    ? conversations.filter((conversation) => !conversation.id?.startsWith('sample-'))
    : []
}

export function readProjects(accountId) {
  const projects = readStoredValue(scopedKey(PROJECTS_KEY, accountId), null)
  return Array.isArray(projects) ? projects : []
}

export function readSettings() {
  return { ...defaultSettings, ...readStoredValue(SETTINGS_KEY, {}) }
}

export function storeConversations(conversations, accountId) {
  try {
    localStorage.setItem(scopedKey(CONVERSATIONS_KEY, accountId), JSON.stringify(conversations))
    return true
  } catch (error) {
    console.error('Could not save CodeMind conversations to local storage.', error)
    return false
  }
}

export function storeProjects(projects, accountId) {
  try {
    localStorage.setItem(scopedKey(PROJECTS_KEY, accountId), JSON.stringify(projects))
    return true
  } catch (error) {
    console.error('Could not save CodeMind projects to local storage.', error)
    return false
  }
}

export function storeSettings(settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
    return true
  } catch (error) {
    console.error('Could not save CodeMind settings to local storage.', error)
    return false
  }
}
