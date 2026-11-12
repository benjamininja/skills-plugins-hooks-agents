import { readFileSync, writeFileSync } from 'node:fs'

import { run } from './queue-edit.ts'

process.exitCode = run(process.argv.slice(2), {
  read: path => readFileSync(path, 'utf8'),
  write: (path, text) => writeFileSync(path, text, 'utf8'),
  print: line => console.log(line),
})
