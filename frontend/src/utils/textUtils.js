export function countWords(html) {
  if (!html) return 0
  const text = html.replace(/<[^>]+>/g, ' ').trim()
  return text ? text.split(/\s+/).filter(Boolean).length : 0
}
