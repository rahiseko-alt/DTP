/** Search registered school photos by caption, ID, and tags; write contact sheets for matches. */
import { runMain } from './lib/cli.ts';
import { photoSearchCommand } from './lib/photo-search.ts';
await runMain(photoSearchCommand);
