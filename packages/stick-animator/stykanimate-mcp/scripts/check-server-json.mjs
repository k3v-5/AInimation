#!/usr/bin/env node
/**
 * Check the registry manifest against the official schema.
 *
 * The schema is fetched, so a machine without a network skips the check
 * rather than failing it.
 */
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { AjvJsonSchemaValidator } from '@modelcontextprotocol/server/validators/ajv';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SCHEMA_URL = 'https://static.modelcontextprotocol.io/schemas/2025-07-09/server.schema.json';

const manifest = JSON.parse(await readFile(path.join(packageRoot, 'server.json'), 'utf8'));

let schema;
try {
  const response = await fetch(SCHEMA_URL);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  schema = await response.json();
} catch (error) {
  console.log(`server.json: the schema could not be fetched (${error.message}); the check was skipped.`);
  process.exit(0);
}

const validator = new AjvJsonSchemaValidator();
const check = await validator.getValidator(schema);
const result = check(manifest);
if (!result.valid) {
  console.error('server.json does not match the registry schema:');
  console.error(JSON.stringify(result.errors, null, 2));
  process.exit(1);
}
console.log('server.json matches the registry schema.');
