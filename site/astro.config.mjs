import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://james-joobs.github.io',
  base: '/awesome-nvidia-physical-ai/',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
  vite: {
    server: {
      fs: {
        allow: [fileURLToPath(new URL('..', import.meta.url))],
      },
    },
  },
});
