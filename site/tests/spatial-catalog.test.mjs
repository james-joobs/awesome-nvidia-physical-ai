import assert from 'node:assert/strict';
import test from 'node:test';
import { availability, licenseLabel } from '../src/lib/catalog-filters.mjs';

test('spatial tools keep code, asset and model access scopes distinct', () => {
  assert.equal(licenseLabel('Public repository; MIT code; CC-BY assets; UE terms separate', 'external'), 'review');
  assert.equal(licenseLabel('Downloadable weights; NVIDIA Internal Scientific Research and Development Model License', 'platform'), 'NVIDIA Internal Scientific Research and Development Model License');
  assert.equal(availability('Downloadable weights; research-only license', '', 'platform'), 'public');
  assert.equal(availability('Public repository; FLUX weights access required', '', 'external'), 'restricted');
  assert.equal(availability('Product / hosted service; paid export terms', '', 'platform'), 'documented');
});
