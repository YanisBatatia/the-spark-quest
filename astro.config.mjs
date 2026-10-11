import { defineConfig } from 'astro/config';

// GitHub Actions provides this for the repository that publishes the site.
const [owner, repository] = (process.env.GITHUB_REPOSITORY ?? '').split('/');
const isUserSite = repository === `${owner}.github.io`;

export default defineConfig({
  site: owner ? `https://${owner}.github.io` : 'http://localhost:4321',
  base: repository && !isUserSite ? `/${repository}/` : '/',
  output: 'static',
});
