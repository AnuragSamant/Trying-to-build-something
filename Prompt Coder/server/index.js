import 'dotenv/config'
import { createServer } from 'node:http'
import { createHash, randomBytes, scrypt as scryptCallback, timingSafeEqual } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { promisify } from 'node:util'
import { DatabaseSync } from 'node:sqlite'

const scrypt = promisify(scryptCallback)
const port = Number(process.env.API_PORT || 3002)
const schemaPath = fileURLToPath(new URL('./schema.sql', import.meta.url))
const databasePath = fileURLToPath(new URL('./codemind.sqlite', import.meta.url))
const maxRequestBytes = 10 * 1024 * 1024
const sessionCookie = 'codemind_session'
const sessionDurationSeconds = 60 * 60 * 24 * 30
const database = new DatabaseSync(databasePath)
database.exec('PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;')

function sqliteStatement(sql, params = []) {
  const values = []
  const statement = sql.replace(/\$(\d+)/g, (_match, index) => {
    values.push(params[Number(index) - 1])
    return '?'
  })
  return [statement, values]
}

const pool = {
  async query(sql, params = []) {
    const [statement, values] = sqliteStatement(sql, params)
    const prepared = database.prepare(statement)
    if (/^\s*(SELECT|WITH|PRAGMA)/i.test(statement)) {
      const rows = prepared.all(...values)
      return { rows, rowCount: rows.length }
    }
    const result = prepared.run(...values)
    return { rows: [], rowCount: Number(result.changes), lastInsertRowid: result.lastInsertRowid }
  },
  async connect() {
    return {
      query: pool.query,
      beginTransaction: () => database.exec('BEGIN IMMEDIATE'),
      commit: () => database.exec('COMMIT'),
      rollback: () => database.exec('ROLLBACK'),
      release() {},
    }
  },
  end() { database.close() },
}

function httpError(status, message) {
  const error = new Error(message)
  error.status = status
  return error
}

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function requireText(value, label, maxLength, allowEmpty = false) {
  if (typeof value !== 'string' || value.length > maxLength || (!allowEmpty && !value.trim())) {
    throw httpError(400, `${label} must be a${allowEmpty ? ' string' : ' non-empty string'} of at most ${maxLength} characters.`)
  }
  return value
}

function requireDate(value, label) {
  if (typeof value !== 'string' || Number.isNaN(Date.parse(value))) {
    throw httpError(400, `${label} must be a valid date string.`)
  }
  return new Date(value).toISOString()
}

function asIsoString(value) {
  return value instanceof Date ? value.toISOString() : new Date(value).toISOString()
}

function publicUser(row) {
  return { id: row.id, email: row.email, name: row.display_name }
}

function getSessionToken(request) {
  const cookies = request.headers.cookie?.split(';') || []
  for (const cookie of cookies) {
    const separator = cookie.indexOf('=')
    if (separator < 0) continue
    if (cookie.slice(0, separator).trim() === sessionCookie) {
      return decodeURIComponent(cookie.slice(separator + 1).trim())
    }
  }
  return null
}

function sessionCookieHeader(token, maxAge) {
  const secure = process.env.COOKIE_SECURE === 'true'
  return `${sessionCookie}=${encodeURIComponent(token)}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${maxAge}${secure ? '; Secure' : ''}`
}

async function createSession(userId, database = pool) {
  const token = randomBytes(32).toString('base64url')
  const tokenHash = createHash('sha256').update(token).digest('hex')
  const expiresAt = new Date(Date.now() + sessionDurationSeconds * 1000).toISOString()
  await database.query(
    'INSERT INTO sessions (token_hash, user_id, expires_at) VALUES ($1, $2, $3)',
    [tokenHash, userId, expiresAt],
  )
  return sessionCookieHeader(token, sessionDurationSeconds)
}

async function authenticatedUser(request) {
  const token = getSessionToken(request)
  if (!token) return null
  const tokenHash = createHash('sha256').update(token).digest('hex')
  const result = await pool.query(
    `SELECT users.id, users.email, users.display_name
     FROM sessions JOIN users ON users.id = sessions.user_id
     WHERE sessions.token_hash = $1 AND sessions.expires_at > strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`,
    [tokenHash],
  )
  return result.rows[0] || null
}

async function claimLegacyWorkspace(userId, client) {
  await client.query('UPDATE projects SET user_id = $1 WHERE user_id IS NULL', [userId])
  await client.query('UPDATE conversations SET user_id = $1 WHERE user_id IS NULL', [userId])
}

async function registerAccount(body, response) {
  if (!isRecord(body)) throw httpError(400, 'Request body must be an object.')
  const email = requireText(body.email, 'Email', 254).trim().toLowerCase()
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw httpError(400, 'Enter a valid email address.')
  const password = requireText(body.password, 'Password', 200)
  if (password.length < 8) throw httpError(400, 'Password must contain at least 8 characters.')
  const userId = randomBytes(16).toString('hex')
  const salt = randomBytes(16)
  const passwordHash = (await scrypt(password, salt, 64)).toString('hex')
  const client = await pool.connect()
  try {
    await client.beginTransaction()
    await client.query(
      "INSERT INTO users (id, email, password_hash, display_name, created_at) VALUES ($1, $2, $3, NULL, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))",
      [userId, email, `${salt.toString('hex')}:${passwordHash}`],
    )
    const account = await client.query('SELECT id, email, display_name FROM users WHERE id = $1', [userId])
    await claimLegacyWorkspace(userId, client)
    const cookie = await createSession(userId, client)
    await client.commit()
    response.setHeader('Set-Cookie', cookie)
    return { user: publicUser(account.rows[0]) }
  } catch (error) {
    try {
      await client.rollback()
    } catch (rollbackError) {
      console.error('Could not roll back account registration.', rollbackError)
    }
    if (error.code === 'ERR_SQLITE_CONSTRAINT_UNIQUE') throw httpError(409, 'An account with that email already exists.')
    throw error
  } finally {
    client.release()
  }
}

async function loginAccount(body, response) {
  if (!isRecord(body)) throw httpError(400, 'Request body must be an object.')
  const email = requireText(body.email, 'Email', 254).trim().toLowerCase()
  const password = requireText(body.password, 'Password', 200)
  const result = await pool.query(
    'SELECT id, email, password_hash, display_name FROM users WHERE LOWER(email) = $1',
    [email],
  )
  const user = result.rows[0]
  if (!user) throw httpError(401, 'Email or password is incorrect.')
  const [saltHex, hashHex] = user.password_hash.split(':')
  const expected = Buffer.from(hashHex || '', 'hex')
  const actual = await scrypt(password, Buffer.from(saltHex || '', 'hex'), expected.length)
  if (!expected.length || !timingSafeEqual(expected, actual)) {
    throw httpError(401, 'Email or password is incorrect.')
  }
  response.setHeader('Set-Cookie', await createSession(user.id))
  return { user: publicUser(user) }
}

async function updateDisplayName(userId, body) {
  if (!isRecord(body)) throw httpError(400, 'Request body must be an object.')
  const name = requireText(body.name, 'Name', 80).trim()
  await pool.query('UPDATE users SET display_name = $1 WHERE id = $2', [name, userId])
  const result = await pool.query('SELECT id, email, display_name FROM users WHERE id = $1', [userId])
  if (!result.rowCount) throw httpError(404, 'Account not found.')
  return publicUser(result.rows[0])
}

function validateWorkspace(body) {
  if (!isRecord(body) || !Array.isArray(body.projects) || !Array.isArray(body.conversations)) {
    throw httpError(400, 'Workspace must contain project and conversation arrays.')
  }

  const projectIds = new Set()
  const projects = body.projects.map((project) => {
    if (!isRecord(project)) throw httpError(400, 'Each project must be an object.')
    const id = requireText(project.id, 'Project ID', 100)
    if (projectIds.has(id)) throw httpError(400, `Duplicate project ID "${id}".`)
    projectIds.add(id)
    return {
      id,
      name: requireText(project.name, 'Project name', 60),
      description: requireText(project.description ?? '', 'Project description', 180, true),
      instructions: requireText(project.instructions ?? '', 'Project instructions', 3000, true),
      createdAt: requireDate(project.createdAt, 'Project createdAt'),
    }
  })

  const conversationIds = new Set()
  const messageIds = new Set()
  let messageCount = 0
  const conversations = body.conversations.map((conversation) => {
    if (!isRecord(conversation) || !Array.isArray(conversation.messages)) {
      throw httpError(400, 'Each conversation must have a message array.')
    }
    const id = requireText(conversation.id, 'Conversation ID', 100)
    if (conversationIds.has(id)) throw httpError(400, `Duplicate conversation ID "${id}".`)
    conversationIds.add(id)
    const projectId = conversation.projectId || null
    if (projectId !== null && (typeof projectId !== 'string' || !projectIds.has(projectId))) {
      throw httpError(400, `Conversation "${id}" references an unknown project.`)
    }
    const messages = conversation.messages.map((message) => {
      if (!isRecord(message)) throw httpError(400, 'Each message must be an object.')
      const messageId = requireText(message.id, 'Message ID', 100)
      if (messageIds.has(messageId)) throw httpError(400, `Duplicate message ID "${messageId}".`)
      messageIds.add(messageId)
      messageCount += 1
      if (messageCount > 10000) throw httpError(413, 'Workspace contains too many messages.')
      if (!['user', 'assistant'].includes(message.role)) throw httpError(400, 'Message role must be user or assistant.')
      const status = message.status ?? 'done'
      if (!['thinking', 'streaming', 'done', 'error'].includes(status)) {
        throw httpError(400, 'Message status is invalid.')
      }
      const rawAttachments = message.attachments ?? []
      if (!Array.isArray(rawAttachments) || rawAttachments.length > 20 || rawAttachments.some((attachment) => !isRecord(attachment))) {
        throw httpError(400, 'Message attachments must be an array of objects.')
      }
      const attachments = rawAttachments.map((attachment) => {
        if (!Number.isSafeInteger(attachment.size) || attachment.size < 0) {
          throw httpError(400, 'Attachment size must be a non-negative integer.')
        }
        return {
          name: requireText(attachment.name, 'Attachment name', 255),
          extension: requireText(attachment.extension ?? 'FILE', 'Attachment extension', 20),
          mimeType: requireText(attachment.mimeType ?? '', 'Attachment MIME type', 150, true),
          size: attachment.size,
        }
      })
      return {
        id: messageId,
        role: message.role,
        content: requireText(message.content ?? '', 'Message content', 200000, true),
        status,
        createdAt: requireDate(message.createdAt, 'Message createdAt'),
        attachments,
      }
    })
    return {
      id,
      projectId,
      title: requireText(conversation.title, 'Conversation title', 200),
      updatedAt: requireDate(conversation.updatedAt, 'Conversation updatedAt'),
      messages,
    }
  })

  return { projects, conversations }
}

async function readJson(request) {
  const chunks = []
  let size = 0
  for await (const chunk of request) {
    size += chunk.length
    if (size > maxRequestBytes) throw httpError(413, 'Request body is too large.')
    chunks.push(chunk)
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'))
  } catch {
    throw httpError(400, 'Request body must be valid JSON.')
  }
}

async function readWorkspace(userId) {
  const [projectResult, conversationResult, messageResult] = await Promise.all([
    pool.query('SELECT id, name, description, instructions, created_at FROM projects WHERE user_id = $1 ORDER BY created_at DESC', [userId]),
    pool.query('SELECT id, project_id, title, updated_at FROM conversations WHERE user_id = $1 ORDER BY updated_at DESC', [userId]),
    pool.query(
      `SELECT messages.id, messages.conversation_id, messages.role, messages.content, messages.status, messages.created_at, messages.attachments
       FROM messages JOIN conversations ON conversations.id = messages.conversation_id
       WHERE conversations.user_id = $1 ORDER BY messages.created_at`,
      [userId],
    ),
  ])
  const messagesByConversation = new Map()
  for (const row of messageResult.rows) {
    const messages = messagesByConversation.get(row.conversation_id) || []
    messages.push({
      id: row.id,
      role: row.role,
      content: row.content,
      status: row.status,
      createdAt: asIsoString(row.created_at),
      attachments: JSON.parse(row.attachments),
    })
    messagesByConversation.set(row.conversation_id, messages)
  }
  return {
    projects: projectResult.rows.map((row) => ({
      id: row.id,
      name: row.name,
      description: row.description,
      instructions: row.instructions,
      createdAt: asIsoString(row.created_at),
    })),
    conversations: conversationResult.rows.map((row) => ({
      id: row.id,
      projectId: row.project_id,
      title: row.title,
      updatedAt: asIsoString(row.updated_at),
      messages: messagesByConversation.get(row.id) || [],
    })),
  }
}

async function writeWorkspace(userId, body) {
  const workspace = validateWorkspace(body)
  const client = await pool.connect()
  try {
    await client.beginTransaction()
    for (const project of workspace.projects) {
      const existing = await client.query('SELECT user_id FROM projects WHERE id = $1', [project.id])
      if (existing.rowCount && existing.rows[0].user_id !== userId) throw httpError(409, 'A project ID conflicts with another account.')
      if (existing.rowCount) {
        await client.query(
          'UPDATE projects SET name = $1, description = $2, instructions = $3, created_at = $4 WHERE id = $5 AND user_id = $6',
          [project.name, project.description, project.instructions, project.createdAt, project.id, userId],
        )
      } else {
        await client.query(
          'INSERT INTO projects (id, name, description, instructions, created_at, user_id) VALUES ($1, $2, $3, $4, $5, $6)',
          [project.id, project.name, project.description, project.instructions, project.createdAt, userId],
        )
      }
    }
    for (const conversation of workspace.conversations) {
      const existing = await client.query('SELECT user_id FROM conversations WHERE id = $1', [conversation.id])
      if (existing.rowCount && existing.rows[0].user_id !== userId) throw httpError(409, 'A conversation ID conflicts with another account.')
      if (existing.rowCount) {
        await client.query(
          'UPDATE conversations SET project_id = $1, title = $2, updated_at = $3 WHERE id = $4 AND user_id = $5',
          [conversation.projectId, conversation.title, conversation.updatedAt, conversation.id, userId],
        )
      } else {
        await client.query(
          'INSERT INTO conversations (id, project_id, title, updated_at, user_id) VALUES ($1, $2, $3, $4, $5)',
          [conversation.id, conversation.projectId, conversation.title, conversation.updatedAt, userId],
        )
      }
    }
    for (const conversation of workspace.conversations) {
      for (const message of conversation.messages) {
        const existing = await client.query(
          'SELECT conversations.user_id FROM messages JOIN conversations ON conversations.id = messages.conversation_id WHERE messages.id = $1',
          [message.id],
        )
        if (existing.rowCount && existing.rows[0].user_id !== userId) throw httpError(409, 'A message ID conflicts with another account.')
        const values = [conversation.id, message.role, message.content, message.status, message.createdAt, JSON.stringify(message.attachments), message.id]
        if (existing.rowCount) {
          await client.query(
            'UPDATE messages SET conversation_id = $1, role = $2, content = $3, status = $4, created_at = $5, attachments = $6 WHERE id = $7',
            values,
          )
        } else {
          await client.query(
            'INSERT INTO messages (conversation_id, role, content, status, created_at, attachments, id) VALUES ($1, $2, $3, $4, $5, $6, $7)',
            values,
          )
        }
      }
    }
    const messageIds = workspace.conversations.flatMap((item) => item.messages.map((message) => message.id))
    const conversationIds = workspace.conversations.map((item) => item.id)
    const projectIds = workspace.projects.map((item) => item.id)
    const deleteExcept = async (sql, ids) => {
      const placeholders = ids.map((_, index) => `$${index + 2}`).join(', ')
      const exclusion = ids.length ? ` AND id NOT IN (${placeholders})` : ''
      await client.query(`${sql}${exclusion}`, [userId, ...ids])
    }
    const messagePlaceholders = messageIds.map((_, index) => `$${index + 2}`).join(', ')
    await client.query(
      `DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = $1)${messageIds.length ? ` AND id NOT IN (${messagePlaceholders})` : ''}`,
      [userId, ...messageIds],
    )
    await deleteExcept('DELETE FROM conversations WHERE user_id = $1', conversationIds)
    await deleteExcept('DELETE FROM projects WHERE user_id = $1', projectIds)
    await client.commit()
  } catch (error) {
    try {
      await client.rollback()
    } catch (rollbackError) {
      console.error('Could not roll back the SQLite workspace transaction.', rollbackError)
    }
    throw error
  } finally {
    client.release()
  }
}

const server = createServer(async (request, response) => {
  const url = new URL(request.url, 'http://localhost')
  response.setHeader('Content-Type', 'application/json; charset=utf-8')
  try {
    if (request.method === 'GET' && url.pathname === '/api/health') {
      await pool.query('SELECT 1')
      response.writeHead(200).end(JSON.stringify({ status: 'ok' }))
      return
    }
    if (request.method === 'POST' && url.pathname === '/api/auth/signup') {
      const result = await registerAccount(await readJson(request), response)
      response.writeHead(201).end(JSON.stringify(result))
      return
    }
    if (request.method === 'POST' && url.pathname === '/api/auth/login') {
      const result = await loginAccount(await readJson(request), response)
      response.writeHead(200).end(JSON.stringify(result))
      return
    }
    if (request.method === 'POST' && url.pathname === '/api/auth/logout') {
      const token = getSessionToken(request)
      if (token) {
        await pool.query('DELETE FROM sessions WHERE token_hash = $1', [createHash('sha256').update(token).digest('hex')])
      }
      response.setHeader('Set-Cookie', sessionCookieHeader('', 0))
      response.writeHead(200).end(JSON.stringify({ status: 'signed_out' }))
      return
    }
    if (request.method === 'GET' && url.pathname === '/api/auth/me') {
      const user = await authenticatedUser(request)
      response.writeHead(200).end(JSON.stringify({ user: user ? publicUser(user) : null }))
      return
    }
    if (request.method === 'PUT' && url.pathname === '/api/auth/profile') {
      const user = await authenticatedUser(request)
      if (!user) throw httpError(401, 'Sign in to continue.')
      response.writeHead(200).end(JSON.stringify({ user: await updateDisplayName(user.id, await readJson(request)) }))
      return
    }
    if (url.pathname === '/api/workspace') {
      const user = await authenticatedUser(request)
      if (!user) throw httpError(401, 'Sign in to access your workspace.')
      if (request.method === 'GET') {
        response.writeHead(200).end(JSON.stringify(await readWorkspace(user.id)))
        return
      }
      if (request.method === 'PUT') {
        await writeWorkspace(user.id, await readJson(request))
        response.writeHead(200).end(JSON.stringify({ status: 'saved' }))
        return
      }
    }
    response.writeHead(404).end(JSON.stringify({ error: 'API route not found.' }))
  } catch (error) {
    console.error('CodeMind API request failed.', error)
    const status = error.status || 500
    response.writeHead(status).end(JSON.stringify({
      error: status < 500 ? error.message : 'The API could not complete the request. Check the server logs.',
    }))
  }
})

async function start() {
  const schema = await readFile(schemaPath, 'utf8')
  database.exec(schema)
  server.listen(port, '127.0.0.1', () => {
    console.log(`CodeMind API listening at http://127.0.0.1:${port}; SQLite database: ${databasePath}`)
  })
}

start().catch(async (error) => {
  console.error('Could not start the CodeMind API.', error)
  await pool.end()
  process.exitCode = 1
})
