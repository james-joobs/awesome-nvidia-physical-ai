const aliases = [
  [/아이작[\s_-]*심|\bisaac[\s_-]*sim\b/gu, 'isaac sim'],
  [/아이작[\s_-]*랩|\bisaac[\s_-]*lab\b/gu, 'isaac lab'],
  [/알파[\s_-]*심|\balpa[\s_-]*sim\b/gu, 'alpasim'],
  [/알파[\s_-]*마요|\balph?a[\s_-]*mayo\b/gu, 'alpamayo'],
  [/그루트|\bgr00t/gu, 'groot'],
  [/코스모스/gu, 'cosmos'],
  [/뉴턴/gu, 'newton'],
  [/심[\s_-]*레디|\bsim[\s_-]*ready\b/gu, 'simready'],
  [/파이(?=$|[^\p{L}])|π/gu, 'pi'],
  [/\bpi[\s*_-]*(?=\d)/gu, 'pi'],
];

function normalize(value) {
  let text = value.normalize('NFKC').toLowerCase();
  for (const [pattern, replacement] of aliases) text = text.replace(pattern, replacement);
  return text.match(/[\p{L}\p{N}]+(?:\.\d+)*/gu)?.join(' ') ?? '';
}

export function prepareCatalogSearch(title, text) {
  const name = normalize(title);
  const searchable = normalize(text);
  return { name, titleWords: name.split(' '), words: searchable.split(' ') };
}

function containsTerms(words, terms) {
  return terms.every((term) => {
    if (/\d\.\d|^\d+$/.test(term)) return words.includes(term);
    if (term === 'pi') return words.some((word) => /^pi(?:\d|$)/.test(word));
    return words.some((word) => word.startsWith(term));
  });
}

function ranked(entries, query, namesOnly = false) {
  const terms = query.split(' ');
  return entries
    .map((entry) => {
      if (entry.name === query) return { entry, score: 0 };
      if (containsTerms(entry.titleWords, terms)) {
        return { entry, score: entry.name.startsWith(query) ? 1 : 2 };
      }
      return { entry, score: !namesOnly && containsTerms(entry.words, terms) ? 3 : -1 };
    })
    .filter(({ score }) => score >= 0)
    .sort((a, b) => a.score - b.score)
    .map(({ entry }) => entry);
}

export function searchCatalog(entries, value) {
  const query = normalize(value);
  if (!query) return { matches: entries, broader: false };

  const matches = ranked(entries, query);
  if (matches.length) return { matches, broader: false };

  // A release number may not be indexed by the catalog entry for its project.
  const name = query.replace(/ v?\d+(?:\.\d+)+$/, '');
  const broaderMatches = name === query ? [] : ranked(entries, name, true);
  return { matches: broaderMatches, broader: broaderMatches.length > 0 };
}
