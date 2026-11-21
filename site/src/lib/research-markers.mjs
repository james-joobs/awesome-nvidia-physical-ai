// Review event IDs belong to the source documents, not the rendered lessons.
const marker = /[\t ]*<!--\s*research-events?:[a-f0-9, ]+\s*-->/g;

export function hideResearchMarkers(markdown) {
  markdown.core.ruler.after('inline', 'hide_research_markers', (state) => {
    const visit = (tokens) => {
      for (const token of tokens) {
        if (token.type === 'text') token.content = token.content.replace(marker, '');
        if (token.children) visit(token.children);
      }
    };
    visit(state.tokens);
  });
}
