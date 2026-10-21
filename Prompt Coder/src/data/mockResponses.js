function renderExplanation(enabled, style, brief, lines) {
  if (!enabled) return ''
  if (style !== 'line-by-line') return `**Main function:** ${brief}`
  return `**Line-by-line:**\n\n${lines.map(([line, explanation], index) => `${index + 1}. \`${line}\` — ${explanation}`).join('\n')}`
}

export function createMockResponse(prompt, { explainWhileCoding = false, explanationStyle = 'brief' } = {}) {
  const normalized = prompt.toLowerCase()

  if (normalized.includes('simulate error') || normalized.includes('trigger error')) {
    throw new Error('This is a demonstration error state.')
  }

  if (normalized.includes('empty response')) return ''

  if (normalized.includes('factorial') || normalized.includes('python')) {
    return `Here’s a recursive Python factorial function. The base case stops the recursion at 1:

\`\`\`python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    '`factorial` computes a number’s factorial recursively, stopping at 1 and multiplying by the result of each smaller call.',
    [
      ['def factorial(n):', 'Defines a function that accepts the number `n`.'],
      ['    if n <= 1:', 'Checks whether `n` has reached the recursion stopping point.'],
      ['        return 1', 'Returns 1 for the base case so recursion can finish.'],
      ['    return n * factorial(n - 1)', 'Calls the function with `n - 1` and multiplies that result by `n`.'],
      ['print(factorial(5))  # 120', 'Runs the function with 5 and prints the result, 120.'],
    ])}

For production code, you may also want to reject negative input or use an iterative implementation for very large values.`
  }

  if (normalized.includes('rest api') || normalized.includes('api')) {
    return `A small REST endpoint should validate input and return a predictable status code. Here’s a frontend demo snippet (it is not connected to a server):

\`\`\`js
app.get('/api/projects/:id', (req, res) => {
  const project = projects.find((item) => item.id === req.params.id)
  if (!project) return res.status(404).json({ error: 'Project not found' })
  return res.json(project)
})
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    'The route finds a project by its URL ID, returns 404 if it does not exist, and otherwise sends it as JSON.',
    [
      ["app.get('/api/projects/:id', (req, res) => {", 'Registers a GET route with an `id` path parameter.'],
      ['  const project = projects.find((item) => item.id === req.params.id)', 'Searches for the project whose ID matches the URL parameter.'],
      ["  if (!project) return res.status(404).json({ error: 'Project not found' })", 'Returns a 404 JSON error if no matching project exists.'],
      ['  return res.json(project)', 'Sends the matching project as a JSON response.'],
      ['})', 'Closes the route handler.'],
    ])}

Keep this route handler in your server layer and centralize error handling as the application grows.`
  }

  if (normalized.includes('website') || normalized.includes('build') || normalized.includes('html') || normalized.includes('css')) {
    return `A good first step is to create the page structure in HTML, style it with CSS, then add behavior with JavaScript:

\`\`\`html
<article class="feature-card">
  <h2>Feature title</h2>
  <p>A short description of what it does.</p>
</article>
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    'The HTML defines a feature card with a title and a short description.',
    [
      ['<article class="feature-card">', 'Opens a semantic article and assigns the CSS class used to style it.'],
      ['  <h2>Feature title</h2>', 'Adds a second-level heading for the feature name.'],
      ['  <p>A short description of what it does.</p>', 'Adds supporting descriptive text.'],
      ['</article>', 'Closes the feature card.'],
    ])}

\`\`\`css
.feature-card {
  padding: 1.5rem;
  border-radius: 1rem;
  background: #f1f5ed;
}
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    'The `.feature-card` rule adds spacing, rounded corners, and a contrasting background.',
    [
      ['.feature-card {', 'Starts the style rule for elements with the `feature-card` class.'],
      ['  padding: 1.5rem;', 'Adds space between the card content and its edges.'],
      ['  border-radius: 1rem;', 'Rounds the card corners.'],
      ['  background: #f1f5ed;', 'Sets a pale background color for the card.'],
      ['}', 'Ends the CSS rule.'],
    ])}

\`\`\`js
document.querySelector('.feature-card').addEventListener('click', () => {
  console.log('Feature selected')
})
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    'The JavaScript finds the card and registers a click handler that runs when the user selects it.',
    [
      ["document.querySelector('.feature-card').addEventListener('click', () => {", 'Finds the first feature card and registers a function for its click event.'],
      ["  console.log('Feature selected')", 'Writes a message to the browser console when the card is clicked.'],
      ['})', 'Closes the click handler.'],
    ])}

Keep the HTML semantic, make the layout responsive with CSS, and use JavaScript only for interactions.`
  }

  return `Here’s a practical way to approach that:

1. **Define the expected behavior** and the smallest useful result.
2. **Break the work into a few clear steps.**
3. **Implement one step at a time**, checking the result as you go.

\`\`\`js
function getStarted(task) {
  return task.trim() ? \`Working on: \${task}\` : 'Add a little more detail to get started.'
}
\`\`\`

${renderExplanation(explainWhileCoding, explanationStyle,
    '`getStarted` checks whether the task has non-whitespace text and returns either a progress message or a prompt for more detail.',
    [
      ['function getStarted(task) {', 'Defines a function that receives the task text.'],
      ["  return task.trim() ? `Working on: ${task}` : 'Add a little more detail to get started.'", 'Removes surrounding whitespace, then returns a progress message or an empty-input prompt.'],
      ['}', 'Closes the function.'],
    ])}

If you share the relevant code or the exact behavior you want, I can help shape this into a more specific example.`
}
