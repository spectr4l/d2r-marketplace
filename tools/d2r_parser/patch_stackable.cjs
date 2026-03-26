const fs = require('fs');
const path = require('path');
const vm = require('vm');

const RUNE_NAMES = {
  r01: 'El Rune',
  r02: 'Eld Rune',
  r03: 'Tir Rune',
  r04: 'Nef Rune',
  r05: 'Eth Rune',
  r06: 'Ith Rune',
  r07: 'Tal Rune',
  r08: 'Ral Rune',
  r09: 'Ort Rune',
  r10: 'Thul Rune',
  r11: 'Amn Rune',
  r12: 'Sol Rune',
  r13: 'Shael Rune',
  r14: 'Dol Rune',
  r15: 'Hel Rune',
  r16: 'Io Rune',
  r17: 'Lum Rune',
  r18: 'Ko Rune',
  r19: 'Fal Rune',
  r20: 'Lem Rune',
  r21: 'Pul Rune',
  r22: 'Um Rune',
  r23: 'Mal Rune',
  r24: 'Ist Rune',
  r25: 'Gul Rune',
  r26: 'Vex Rune',
  r27: 'Ohm Rune',
  r28: 'Lo Rune',
  r29: 'Sur Rune',
  r30: 'Ber Rune',
  r31: 'Jah Rune',
  r32: 'Cham Rune',
  r33: 'Zod Rune',
};

const RUNE_ORDER = Object.keys(RUNE_NAMES);

function normalizeName(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

function prettyName(item) {
  return item.type_name || RUNE_NAMES[item.type] || item.type || '(sem nome)';
}

function findRuneCodeByName(name) {
  const n = normalizeName(name);
  for (const [code, runeName] of Object.entries(RUNE_NAMES)) {
    if (normalizeName(runeName) === n) return code;
  }
  return null;
}

function isRuneCode(code) {
  return /^r\d{2}$/i.test(String(code || ''));
}

function loadWebpackChunk(file) {
  const modules = {};
  const cache = {};

  const sandbox = {
    self: {
      webpackChunk_N_E: {
        push(chunk) {
          Object.assign(modules, chunk[1]);
        },
      },
    },
    console,
    TextDecoder,
    TextEncoder,
    Uint8Array,
    DataView,
    ArrayBuffer,
    Buffer,
    setTimeout,
    clearTimeout,
  };

  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(file, 'utf8'), sandbox, { filename: file });

  function req(id) {
    if (cache[id]) return cache[id].exports;
    if (!modules[id]) throw new Error(`Módulo ${id} não encontrado`);
    const module = { exports: {} };
    cache[id] = module;
    modules[id](module, module.exports, req);
    return module.exports;
  }

  req.d = (exports, definition) => {
    for (const key in definition) {
      if (!Object.prototype.hasOwnProperty.call(exports, key)) {
        Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
      }
    }
  };

  req.r = (exports) => {
    Object.defineProperty(exports, '__esModule', { value: true });
  };

  req.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop);

  req.n = (mod) => {
    const getter = mod && mod.__esModule ? () => mod.default : () => mod;
    req.d(getter, { a: getter });
    return getter;
  };

  return req;
}

function splitLegacyD2IPages(buffer, maxPages = 6) {
  const pages = [];
  let offset = 0;

  for (let i = 0; i < maxPages; i++) {
    if (offset + 64 > buffer.length) break;

    const magic = buffer.readUInt32LE(offset);
    if (magic !== 0xaa55aa55) break;

    const size = buffer.readUInt32LE(offset + 16);
    if (!size || offset + size > buffer.length) {
      throw new Error(`Tamanho de página inválido em offset ${offset}: ${size}`);
    }

    pages.push({
      index: i,
      offset,
      size,
      isStackable: buffer.readUInt8(offset + 20),
      data: Buffer.from(buffer.subarray(offset, offset + size)),
    });

    offset += size;
  }

  return {
    pages,
    tail: Buffer.from(buffer.subarray(offset)),
  };
}

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

function usage() {
  console.log(`
Uso:
  node patch_stackable.cjs input.d2i output.d2i <code|nome> <quantidade> [--create]

Exemplos:
  node patch_stackable.cjs sharedstash.d2i out.d2i r31 50
  node patch_stackable.cjs sharedstash.d2i out.d2i "Jah Rune" 50
  node patch_stackable.cjs sharedstash.d2i out.d2i r33 1 --create
  node patch_stackable.cjs sharedstash.d2i out.d2i "Zod Rune" 1 --create

Observações:
  - Sem --create: só altera item já existente.
  - Com --create: tenta criar clonando um stackable parecido.
  - Para runas altas como r32/r33, o modo --create é experimental, mas é uma boa base.
`);
}

function resolveTarget(rawTarget) {
  const byName = findRuneCodeByName(rawTarget);
  const code = byName || String(rawTarget).trim().toLowerCase();

  return {
    raw: rawTarget,
    code,
    displayName: RUNE_NAMES[code] || rawTarget,
  };
}

function listItems(items) {
  console.log('Itens disponíveis:');
  items.forEach((i) => {
    const amount = i.amount_in_shared_stash ?? 0;
    console.log(`- ${i.type} | ${prettyName(i)} | qtd=${amount}`);
  });
}

function findItem(items, target) {
  const wantedName = normalizeName(target.raw);
  const wantedCode = normalizeName(target.code);

  return items.find((item) => {
    const itemType = normalizeName(item.type);
    const itemName = normalizeName(prettyName(item));
    return itemType === wantedCode || itemName === wantedName;
  });
}

function pickTemplateForCreate(items, targetCode) {
  if (isRuneCode(targetCode)) {
    const runeItems = items.filter((i) => isRuneCode(i.type));
    if (!runeItems.length) return null;

    const wantedIdx = RUNE_ORDER.indexOf(targetCode);
    if (wantedIdx === -1) return runeItems[runeItems.length - 1];

    let best = runeItems[0];
    let bestDist = Number.POSITIVE_INFINITY;

    for (const item of runeItems) {
      const idx = RUNE_ORDER.indexOf(item.type);
      if (idx === -1) continue;
      const dist = Math.abs(idx - wantedIdx);
      if (dist < bestDist) {
        best = item;
        bestDist = dist;
      }
    }

    return best;
  }

  return items[0] || null;
}

function createNewStackableFromTemplate(template, targetCode, amount) {
  const cloned = deepClone(template);

  cloned.type = targetCode;
  cloned.type_name = RUNE_NAMES[targetCode] || cloned.type_name || targetCode;
  cloned.amount_in_shared_stash = amount;

  if (cloned._unknown_data == null || typeof cloned._unknown_data !== 'object') {
    cloned._unknown_data = {};
  }
  cloned._unknown_data.chest_stackable = 1;

  if (typeof cloned.simple_item === 'undefined') cloned.simple_item = 1;
  if (typeof cloned.identified === 'undefined') cloned.identified = 1;
  if (typeof cloned.socketed === 'undefined') cloned.socketed = 0;
  if (typeof cloned.new === 'undefined') cloned.new = 0;
  if (typeof cloned.is_ear === 'undefined') cloned.is_ear = 0;
  if (typeof cloned.ethereal === 'undefined') cloned.ethereal = 0;
  if (typeof cloned.personalized === 'undefined') cloned.personalized = 0;
  if (typeof cloned.given_runeword === 'undefined') cloned.given_runeword = 0;
  if (typeof cloned.nr_of_items_in_sockets === 'undefined') cloned.nr_of_items_in_sockets = 0;
  if (typeof cloned.version === 'undefined') cloned.version = 105;

  return cloned;
}

(async () => {
  const input = process.argv[2];
  const output = process.argv[3];
  const rawTarget = process.argv[4];
  const amount = Number(process.argv[5] || 1);
  const createMode = process.argv.includes('--create');

  if (!input || !output || !rawTarget || !Number.isFinite(amount) || amount < 0) {
    usage();
    process.exit(1);
  }

  const target = resolveTarget(rawTarget);

  const base = __dirname;
  const stashChunk = path.join(base, '3948-158edc89d00d35f1.js');
  const constantsChunk = path.join(base, '385ca0d5-aecd714f7b16aad0.js');

  if (!fs.existsSync(input)) throw new Error(`Arquivo não encontrado: ${input}`);
  if (!fs.existsSync(stashChunk)) throw new Error(`Chunk não encontrado: ${stashChunk}`);
  if (!fs.existsSync(constantsChunk)) throw new Error(`Chunk não encontrado: ${constantsChunk}`);

  const stashReq = loadWebpackChunk(stashChunk);
  const constReq = loadWebpackChunk(constantsChunk);

  const itemsMod = stashReq(61995);
  const BitReader = stashReq(76116).BitReader;
  const constants = constReq(4258).A;

  const buffer = fs.readFileSync(input);
  const { pages, tail } = splitLegacyD2IPages(buffer);

  if (!pages.length) throw new Error('Nenhuma página legacy encontrada no .d2i');

  const stackPage = pages.find((p) => p.isStackable === 1);
  if (!stackPage) throw new Error('Página stackable não encontrada');

  const header = Buffer.from(stackPage.data.subarray(0, 64));
  const itemBytes = stackPage.data.subarray(64);

  const items = await itemsMod.readItems(
    new BitReader(itemBytes),
    105,
    constants,
    { extendedStash: false }
  );

  let found = findItem(items, target);

  if (found) {
    console.log(`✔ Encontrado: ${prettyName(found)} (${found.type})`);
    console.log(`Quantidade atual: ${found.amount_in_shared_stash ?? 0}`);
    found.amount_in_shared_stash = amount;
    console.log(`Nova quantidade: ${amount}`);
  } else if (createMode) {
    console.log(`⚠ Item não encontrado no stash: ${target.displayName} (${target.code})`);
    console.log('Tentando criar via clone de template...');

    const template = pickTemplateForCreate(items, target.code);
    if (!template) {
      console.log('❌ Não foi encontrado nenhum template stackable para clonar.');
      process.exit(1);
    }

    console.log(`Template usado: ${prettyName(template)} (${template.type})`);

    const created = createNewStackableFromTemplate(template, target.code, amount);
    items.push(created);

    console.log(`✔ Item criado: ${prettyName(created)} (${created.type})`);
    console.log(`Quantidade inicial: ${created.amount_in_shared_stash}`);
  } else {
    console.log(`❌ Item não encontrado no stash stackable atual: ${target.displayName} (${target.code})`);
    console.log('Esse script só altera itens já existentes, a menos que você use --create.');
    listItems(items);
    process.exit(1);
  }

  const rewrittenItems = await itemsMod.writeItems(items, 105, constants, {
    extendedStash: false,
  });

  const newPage = Buffer.concat([header, Buffer.from(rewrittenItems)]);
  newPage.writeUInt32LE(newPage.length, 16);

  const final = Buffer.concat(
    pages.map((p) => (p.index === stackPage.index ? newPage : p.data)).concat(tail)
  );

  fs.writeFileSync(output, final);

  console.log(`💾 Salvo em: ${output}`);
})();