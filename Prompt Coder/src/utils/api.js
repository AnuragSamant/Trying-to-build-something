async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.error || `Request failed with HTTP ${response.status}.`)
  }
  return payload
}

export function loadWorkspace() {
  return request('/api/workspace')
}

export function getCurrentUser() {
  return request('/api/auth/me')
}

export function signIn(credentials) {
  return request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function signUp(credentials) {
  return request('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function saveProfile(profile) {
  return request('/api/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(profile),
  })
}

export function signOut() {
  return request('/api/auth/logout', { method: 'POST' })
}

export function saveWorkspace(workspace) {
  return request('/api/workspace', {
    method: 'PUT',
    body: JSON.stringify(workspace),
  })
}
