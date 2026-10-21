const today = new Date()
const yesterday = new Date(today)
yesterday.setDate(today.getDate() - 1)
const earlier = new Date(today)
earlier.setDate(today.getDate() - 3)

const stamp = (date, hour, minute) => {
  const value = new Date(date)
  value.setHours(hour, minute, 0, 0)
  return value.toISOString()
}

export const sampleConversations = [
  {
    id: 'sample-portfolio',
    title: 'Build a portfolio website',
    updatedAt: stamp(today, 10, 42),
    messages: [
      {
        id: 'portfolio-user',
        role: 'user',
        content: 'Create a clean portfolio homepage with HTML, CSS, and JavaScript.',
        createdAt: stamp(today, 10, 39),
      },
      {
        id: 'portfolio-assistant',
        role: 'assistant',
        status: 'done',
        createdAt: stamp(today, 10, 40),
        content: `A strong portfolio homepage can stay simple while still showing personality. Here’s a small starting point using plain HTML, CSS, and JavaScript:

\`\`\`html
<section class="project-grid">
  <article><span>Product design</span><h2>Field Notes</h2></article>
  <article><span>Web application</span><h2>Northstar</h2></article>
</section>
\`\`\`

\`\`\`css
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
\`\`\`

Keep the introduction focused, then let the projects do most of the talking.`,
      },
    ],
  },
  {
    id: 'sample-python',
    title: 'Fix Python error',
    updatedAt: stamp(yesterday, 16, 18),
    messages: [
      {
        id: 'python-user',
        role: 'user',
        content: 'Why do I get a KeyError when reading a dictionary?',
        createdAt: stamp(yesterday, 16, 15),
      },
      {
        id: 'python-assistant',
        role: 'assistant',
        status: 'done',
        createdAt: stamp(yesterday, 16, 16),
        content: `A \`KeyError\` means the key you requested isn't present in the dictionary. Use \`get\` when a missing value is expected:

\`\`\`python
profile = {"name": "Ari"}
city = profile.get("city", "Unknown")
print(city)
\`\`\`

If the key should always exist, check where the dictionary is created and verify the spelling and capitalization of the key.`,
      },
    ],
  },
  {
    id: 'sample-login',
    title: 'Create login page',
    updatedAt: stamp(earlier, 12, 4),
    messages: [
      {
        id: 'login-user',
        role: 'user',
        content: 'What should I include in a polished login page?',
        createdAt: stamp(earlier, 12, 0),
      },
      {
        id: 'login-assistant',
        role: 'assistant',
        status: 'done',
        createdAt: stamp(earlier, 12, 2),
        content: `Prioritize a clear form, a visible password recovery path, and helpful validation close to each field. A semantic form keeps the interaction accessible:

\`\`\`html
<form>
  <label for="email">Email address</label>
  <input id="email" name="email" type="email" autocomplete="email" required />
  <button type="submit">Continue</button>
</form>
\`\`\`

On smaller screens, keep the primary action visible and avoid adding unrelated navigation around the form.`,
      },
    ],
  },
  {
    id: 'sample-recursion',
    title: 'Explain recursion',
    updatedAt: stamp(earlier, 9, 32),
    messages: [
      {
        id: 'recursion-user',
        role: 'user',
        content: 'Explain recursion with a simple example.',
        createdAt: stamp(earlier, 9, 29),
      },
      {
        id: 'recursion-assistant',
        role: 'assistant',
        status: 'done',
        createdAt: stamp(earlier, 9, 30),
        content: `Recursion is when a function solves a problem by calling itself on a smaller version of that problem. It needs a **base case** to stop:

\`\`\`js
function countdown(number) {
  if (number <= 0) return
  console.log(number)
  countdown(number - 1)
}
\`\`\`

Here, \`number <= 0\` is the stopping condition. Without it, the calls would continue until the program ran out of stack space.`,
      },
    ],
  },
  {
    id: 'sample-sql',
    title: 'SQL database design',
    updatedAt: stamp(earlier, 8, 10),
    messages: [
      {
        id: 'sql-user',
        role: 'user',
        content: 'How do I model users and their projects in SQL?',
        createdAt: stamp(earlier, 8, 7),
      },
      {
        id: 'sql-assistant',
        role: 'assistant',
        status: 'done',
        createdAt: stamp(earlier, 8, 8),
        content: `A user can own many projects, so put the user identifier on the project row as a foreign key:

\`\`\`sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  owner_id INTEGER NOT NULL REFERENCES users(id),
  title TEXT NOT NULL
);
\`\`\`

This keeps ownership explicit and lets the database enforce that every project references a real user.`,
      },
    ],
  },
]
