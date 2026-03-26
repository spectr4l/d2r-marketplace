const fs = require("fs");
const path = require("path");
const vm = require("vm");

const RUNE_NAMES = {
  r01: "El Rune",
  r02: "Eld Rune",
  r03: "Tir Rune",
  r04: "Nef Rune",
  r05: "Eth Rune",
  r06: "Ith Rune",
  r07: "Tal Rune",
  r08: "Ral Rune",
  r09: "Ort Rune",
  r10: "Thul Rune",
  r11: "Amn Rune",
  r12: "Sol Rune",
  r13: "Shael Rune",
  r14: "Dol Rune",
  r15: "Hel Rune",
  r16: "Io Rune",
  r17: "Lum Rune",
  r18: "Ko Rune",
  r19: "Fal Rune",
  r20: "Lem Rune",
  r21: "Pul Rune",
  r22: "Um Rune",
  r23: "Mal Rune",
  r24: "Ist Rune",
  r25: "Gul Rune",
  r26: "Vex Rune",
  r27: "Ohm Rune",
  r28: "Lo Rune",
  r29: "Sur Rune",
  r30: "Ber Rune",
  r31: "Jah Rune",
  r32: "Cham Rune",
  r33: "Zod Rune",
};

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
  vm.runInContext(fs.readFileSync(file, "utf8"), sandbox, { filename: file });

  function req(id) {
    if (cache[id]) return cache[id].exports;
    if (!modules[id]) throw new Error(`Módulo ${id} não encontrado em ${file}`);
    const module = { exports: {} };
    cache[id] = module;
    modules[id](module, module.exports, req);
    return module.exports;
  }

  req.d = (exports, definition) => {
    for (const key in definition) {
      if (!Object.prototype.hasOwnProperty.call(exports, key)) {
        Object.defineProperty(exports, key, {
          enumerable: true,
          get: definition[key],
        });
      }
    }
  };

  req.o = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop);

  req.r = (exports) => {
    if (typeof Symbol !== "undefined" && Symbol.toStringTag) {
      Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
    }
    Object.defineProperty(exports, "__esModule", { value: true });
  };

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

    const pageSize = buffer.readUInt32LE(offset + 16);
    if (!pageSize || offset + pageSize > buffer.length) {
      throw new Error(`Tamanho de página inválido em offset ${offset}: ${pageSize}`);
    }

    pages.push({
      index: i,
      offset,
      size: pageSize,
      isStackable: buffer.readUInt8(offset + 20),
      unk0: buffer.readUInt8(offset + 21),
      unk1: buffer.readUInt8(offset + 22),
      unk2: buffer.readUInt8(offset + 23),
      data: Buffer.from(buffer.subarray(offset, offset + pageSize)),
    });

    offset += pageSize;
  }

  return {
    pages,
    tail: Buffer.from(buffer.subarray(offset)),
  };
}

function safeRawItem(item) {
  return {
    id: item.id ?? null,
    type: item.type ?? null,
    type_name: item.type_name ?? null,
    amount_in_shared_stash: item.amount_in_shared_stash ?? null,
    quality: item.quality ?? null,
    simple_item: item.simple_item ?? null,
    identified: item.identified ?? null,
    socketed: item.socketed ?? null,
    ethereal: item.ethereal ?? null,
    position_x: item.position_x ?? null,
    position_y: item.position_y ?? null,
    alt_position_id: item.alt_position_id ?? null,
    location_id: item.location_id ?? null,
    inv_width: item.inv_width ?? null,
    inv_height: item.inv_height ?? null,
    categories: Array.isArray(item.categories) ? item.categories : [],
    level: item.level ?? null,
    version: item.version ?? null,
  };
}

function normalizeItem(item) {
  const type = item.type || null;
  const name = item.type_name || RUNE_NAMES[type] || type || null;

  return {
    id: item.id ?? null,
    type,
    name,
    amount: item.amount_in_shared_stash ?? 1,
    quality: item.quality ?? null,
    simple_item: item.simple_item ?? null,
    identified: item.identified ?? null,
    socketed: item.socketed ?? null,
    ethereal: item.ethereal ?? null,
    position_x: item.position_x ?? null,
    position_y: item.position_y ?? null,
    alt_position_id: item.alt_position_id ?? null,
    location_id: item.location_id ?? null,
    inv_width: item.inv_width ?? null,
    inv_height: item.inv_height ?? null,
    categories: Array.isArray(item.categories) ? item.categories : [],
    level: item.level ?? null,
    version: item.version ?? null,
    raw: safeRawItem(item),
  };
}

(async () => {
  try {
    const inputPath = process.argv[2];
    if (!inputPath) {
      throw new Error("Uso: node read_shared_stash.cjs <arquivo.d2i>");
    }

    const baseDir = __dirname;
    const stashChunk = path.join(baseDir, "3948-158edc89d00d35f1.js");
    const constantsChunk = path.join(baseDir, "385ca0d5-aecd714f7b16aad0.js");

    if (!fs.existsSync(inputPath)) {
      throw new Error(`Arquivo não encontrado: ${inputPath}`);
    }
    if (!fs.existsSync(stashChunk)) {
      throw new Error(`Chunk não encontrado: ${stashChunk}`);
    }
    if (!fs.existsSync(constantsChunk)) {
      throw new Error(`Chunk não encontrado: ${constantsChunk}`);
    }

    const stashReq = loadWebpackChunk(stashChunk);
    const constReq = loadWebpackChunk(constantsChunk);

    const itemsMod = stashReq(61995);
    const BitReader = stashReq(76116).BitReader;
    const constants = constReq(4258).A;

    const buffer = fs.readFileSync(inputPath);
    const { pages, tail } = splitLegacyD2IPages(buffer, 6);

    if (!pages.length) {
      throw new Error("Nenhuma página legacy 0xAA55AA55 encontrada no .d2i");
    }

    const stackablePage = pages.find((p) => p.isStackable === 1);
    if (!stackablePage) {
      throw new Error("Página stackable não encontrada no .d2i");
    }

    const header = stackablePage.data.subarray(0, 64);
    const itemBytes = stackablePage.data.subarray(64);

    const items = await itemsMod.readItems(
      new BitReader(itemBytes),
      105,
      constants,
      { extendedStash: false }
    );

    const normalizedItems = items.map(normalizeItem);

    const result = {
      success: true,
      stash_path: inputPath,
      format: "legacy",
      version: 105,
      pageCount: pages.length,
      tailSize: tail.length,
      stackablePage: {
        index: stackablePage.index,
        size: stackablePage.size,
        isStackable: stackablePage.isStackable,
        headerPreview: Array.from(header.subarray(0, 24)),
      },
      stackables: normalizedItems,
      pages: pages.map((p) => ({
        index: p.index,
        size: p.size,
        isStackable: p.isStackable,
      })),
    };

    process.stdout.write(JSON.stringify(result, null, 2));
  } catch (err) {
    process.stderr.write(
      JSON.stringify(
        {
          success: false,
          error: err?.message || String(err),
          stack: err?.stack || null,
        },
        null,
        2
      )
    );
    process.exit(1);
  }
})();