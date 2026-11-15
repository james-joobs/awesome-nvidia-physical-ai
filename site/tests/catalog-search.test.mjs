import assert from 'node:assert/strict';
import test from 'node:test';
import { prepareCatalogSearch, searchCatalog } from '../src/lib/catalog-search.mjs';

const entry = (title, hints = '') => ({ title, ...prepareCatalogSearch(title, `${title} ${hints}`) });
const entries = [
  entry('isaacsim-assets', 'Sample data for Isaac Sim 6.1'),
  entry('Isaac Sim', 'Robotics simulator · 로봇 시뮬레이터'),
  entry('Isaac Lab', 'Robot learning'),
  entry('Alpamayo 2 Edge code', 'Driving policy'),
  entry('AlpaSim', 'Driving simulation'),
  entry('π₀ / π₀-FAST / π₀.₅'),
  entry('π₀.₆ / π₀.₇', '5 demonstrations'),
  entry('GR00T N1.7', 'Robot model'),
  entry('GR00T N1.70', 'Unrelated version in this fixture'),
  entry('Data pipeline'),
  entry('RTX / DGX Spark', 'graphics processing'),
];
const results = (query) => searchCatalog(entries, query).matches.map(({ title }) => title);

test('exact project names outrank related assets and work across scripts', () => {
  for (const query of ['Isaac Sim', 'IsaacSim', '아이작 심', '아이작심']) {
    assert.equal(results(query)[0], 'Isaac Sim', query);
  }
  assert.deepEqual(results('알파심'), ['AlpaSim']);
  assert.deepEqual(results('alpha mayo'), ['Alpamayo 2 Edge code']);
  assert.deepEqual(results('알파마요'), ['Alpamayo 2 Edge code']);
  assert.deepEqual(results('그루트 N1.7'), ['GR00T N1.7']);
});

test('checkpoint versions stay together and interior substrings do not count', () => {
  for (const query of ['파이0.5', 'π0.5', 'pi 0.5']) {
    assert.deepEqual(results(query), ['π₀ / π₀-FAST / π₀.₅'], query);
  }
  assert.deepEqual(results('phi'), []);
  assert.deepEqual(results('파이'), ['π₀ / π₀-FAST / π₀.₅', 'π₀.₆ / π₀.₇']);
});

test('unknown versions fall back to names without claiming version availability', () => {
  const missing = searchCatalog(entries, 'Isaac Sim v6.2');
  assert.equal(missing.broader, true);
  assert.equal(missing.matches[0].title, 'Isaac Sim');
  const exact = searchCatalog(entries, 'Isaac Sim 6.1');
  assert.equal(exact.broader, false);
  assert.deepEqual(exact.matches.map(({ title }) => title), ['isaacsim-assets']);
  assert.deepEqual(searchCatalog(entries, 'Unknown 20.1'), { matches: [], broader: false });
});

test('blank queries keep filter order and never bring back excluded entries', () => {
  assert.deepEqual(searchCatalog(entries, ' ').matches, entries);
  assert.deepEqual(searchCatalog(entries.filter(({ title }) => title === 'Isaac Lab'), '아이작심').matches, []);
});
