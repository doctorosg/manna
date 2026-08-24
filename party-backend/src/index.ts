import { DurableObject } from "cloudflare:workers";

type RoomPhase = "lobby" | "question" | "reveal" | "finished";

type PartyQuestion = {
  id: string;
  correctIndex: number;
};

type RoomSettings = {
  category: string;
  difficulty: string;
  questionCount: number;
};

type StoredPlayer = {
  id: string;
  token: string;
  name: string;
  score: number;
  answers: Record<string, number>;
};

type StoredRoom = {
  code: string;
  hostPlayerId: string;
  phase: RoomPhase;
  settings: RoomSettings;
  questions: PartyQuestion[];
  currentIndex: number;
  players: StoredPlayer[];
  version: number;
  createdAt: number;
  expiresAt: number;
};

type PublicPlayer = {
  id: string;
  name: string;
  score: number;
  hasAnswered: boolean;
  isHost: boolean;
  wasCorrect: boolean | null;
};

type RoomSnapshot = {
  code: string;
  phase: RoomPhase;
  settings: RoomSettings;
  currentIndex: number;
  questionId: string | null;
  questionNumber: number;
  players: PublicPlayer[];
  answeredCount: number;
  myPlayerId: string;
  myAnswer: number | null;
  isHost: boolean;
  version: number;
};

type SessionResponse = {
  token: string;
  room: RoomSnapshot;
};

const ROOM_TTL_MS = 6 * 60 * 60 * 1000;
const MAX_PLAYERS = 12;
const CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

class PartyError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

export class PartyRoom extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      this.ctx.storage.sql.exec(`
        CREATE TABLE IF NOT EXISTS _sql_schema_migrations (
          id INTEGER PRIMARY KEY,
          applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS room_state (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          state TEXT NOT NULL
        );
        INSERT OR IGNORE INTO _sql_schema_migrations (id) VALUES (1);
      `);
    });
  }

  async initialize(
    code: string,
    hostName: string,
    settings: RoomSettings,
    questions: PartyQuestion[],
  ): Promise<SessionResponse | null> {
    if (this.loadRoom() !== null) return null;
    validateSettings(settings, questions);
    const host = newPlayer(hostName);
    const now = Date.now();
    const room: StoredRoom = {
      code,
      hostPlayerId: host.id,
      phase: "lobby",
      settings,
      questions,
      currentIndex: -1,
      players: [host],
      version: 1,
      createdAt: now,
      expiresAt: now + ROOM_TTL_MS,
    };
    this.saveRoom(room);
    await this.ctx.storage.setAlarm(room.expiresAt);
    return { token: host.token, room: this.snapshotFor(room, host) };
  }

  async join(name: string): Promise<SessionResponse> {
    const room = this.requireRoom();
    if (room.phase !== "lobby") throw new PartyError(409, "This game has already started.");
    if (room.players.length >= MAX_PLAYERS) throw new PartyError(409, "This party is full.");
    const player = newPlayer(name);
    room.players.push(player);
    this.touch(room);
    this.saveRoom(room);
    return { token: player.token, room: this.snapshotFor(room, player) };
  }

  async getSnapshot(token: string): Promise<RoomSnapshot> {
    const room = this.requireRoom();
    const player = authenticate(room, token);
    return this.snapshotFor(room, player);
  }

  async start(token: string): Promise<RoomSnapshot> {
    const room = this.requireRoom();
    const host = authenticateHost(room, token);
    if (room.phase !== "lobby") throw new PartyError(409, "This game has already started.");
    room.currentIndex = 0;
    room.phase = "question";
    this.touch(room);
    this.saveRoom(room);
    return this.snapshotFor(room, host);
  }

  async answer(token: string, answerIndex: number): Promise<RoomSnapshot> {
    const room = this.requireRoom();
    const player = authenticate(room, token);
    if (room.phase !== "question") throw new PartyError(409, "Answers are not open right now.");
    if (!Number.isInteger(answerIndex) || answerIndex < 0 || answerIndex > 5) {
      throw new PartyError(400, "Invalid answer.");
    }
    player.answers[String(room.currentIndex)] = answerIndex;
    this.touch(room);
    this.saveRoom(room);
    return this.snapshotFor(room, player);
  }

  async reveal(token: string): Promise<RoomSnapshot> {
    const room = this.requireRoom();
    const host = authenticateHost(room, token);
    if (room.phase !== "question") throw new PartyError(409, "There is no question to reveal.");
    const correctIndex = room.questions[room.currentIndex]?.correctIndex;
    if (correctIndex === undefined) throw new PartyError(409, "The current question is unavailable.");
    const answerKey = String(room.currentIndex);
    for (const player of room.players) {
      if (player.answers[answerKey] === correctIndex) player.score += 1;
    }
    room.phase = "reveal";
    this.touch(room);
    this.saveRoom(room);
    return this.snapshotFor(room, host);
  }

  async next(token: string): Promise<RoomSnapshot> {
    const room = this.requireRoom();
    const host = authenticateHost(room, token);
    if (room.phase !== "reveal") throw new PartyError(409, "Reveal the answer first.");
    if (room.currentIndex + 1 >= room.questions.length) {
      room.phase = "finished";
    } else {
      room.currentIndex += 1;
      room.phase = "question";
    }
    this.touch(room);
    this.saveRoom(room);
    return this.snapshotFor(room, host);
  }

  async alarm(): Promise<void> {
    await this.ctx.storage.deleteAll();
  }

  private loadRoom(): StoredRoom | null {
    const rows = this.ctx.storage.sql.exec<{ state: string }>(
      "SELECT state FROM room_state WHERE id = 1",
    ).toArray();
    return rows.length === 0 ? null : JSON.parse(rows[0].state) as StoredRoom;
  }

  private requireRoom(): StoredRoom {
    const room = this.loadRoom();
    if (room === null || room.expiresAt <= Date.now()) throw new PartyError(404, "Party not found.");
    return room;
  }

  private saveRoom(room: StoredRoom): void {
    this.ctx.storage.sql.exec(
      "INSERT INTO room_state (id, state) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET state = excluded.state",
      JSON.stringify(room),
    );
  }

  private touch(room: StoredRoom): void {
    room.version += 1;
  }

  private snapshotFor(room: StoredRoom, viewer: StoredPlayer): RoomSnapshot {
    const answerKey = String(room.currentIndex);
    const revealRoundResults = room.phase === "reveal" || room.phase === "finished";
    const correctIndex = room.questions[room.currentIndex]?.correctIndex;
    return {
      code: room.code,
      phase: room.phase,
      settings: room.settings,
      currentIndex: room.currentIndex,
      questionId: room.currentIndex >= 0 ? room.questions[room.currentIndex]?.id ?? null : null,
      questionNumber: room.currentIndex + 1,
      players: room.players
        .map((player) => ({
          id: player.id,
          name: player.name,
          score: player.score,
          hasAnswered: player.answers[answerKey] !== undefined,
          isHost: player.id === room.hostPlayerId,
          wasCorrect: revealRoundResults && correctIndex !== undefined
            ? player.answers[answerKey] === correctIndex
            : null,
        }))
        .sort((a, b) => b.score - a.score || a.name.localeCompare(b.name)),
      answeredCount: room.players.filter((player) => player.answers[answerKey] !== undefined).length,
      myPlayerId: viewer.id,
      myAnswer: viewer.answers[answerKey] ?? null,
      isHost: viewer.id === room.hostPlayerId,
      version: room.version,
    };
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const requestId = crypto.randomUUID();
    const startedAt = Date.now();
    try {
      const response = await route(request, env);
      console.log(JSON.stringify({ level: "info", requestId, method: request.method, path: new URL(request.url).pathname, status: response.status, durationMs: Date.now() - startedAt }));
      return withCors(response);
    } catch (error) {
      const rpcMessage = error instanceof Error ? error.message : "";
      const status = error instanceof PartyError ? error.status : rpcStatus(rpcMessage);
      const message = error instanceof PartyError || status !== 500 ? rpcMessage : "The party service is temporarily unavailable.";
      console.error(JSON.stringify({ level: "error", requestId, status, error: String(error), durationMs: Date.now() - startedAt }));
      return withCors(Response.json({ error: message }, { status }));
    }
  },
} satisfies ExportedHandler<Env>;

async function route(request: Request, env: Env): Promise<Response> {
  if (request.method === "OPTIONS") return new Response(null, { status: 204 });
  const url = new URL(request.url);
  const parts = url.pathname.split("/").filter(Boolean);
  if (parts[0] !== "v1" || parts[1] !== "rooms") throw new PartyError(404, "Not found.");

  if (parts.length === 2 && request.method === "POST") {
    const body = await readJson<{
      hostName?: unknown;
      settings?: RoomSettings;
      questions?: PartyQuestion[];
    }>(request);
    const hostName = cleanName(body.hostName);
    if (!body.settings || !Array.isArray(body.questions)) throw new PartyError(400, "Missing game settings.");
    for (let attempt = 0; attempt < 10; attempt += 1) {
      const code = randomCode();
      const stub = env.PARTY_ROOMS.getByName(code);
      const result = await stub.initialize(code, hostName, body.settings, body.questions);
      if (result !== null) return Response.json(result, { status: 201 });
    }
    throw new PartyError(503, "Could not create a party. Please try again.");
  }

  const code = normalizeCode(parts[2]);
  const stub = env.PARTY_ROOMS.getByName(code);

  if (parts.length === 4 && parts[3] === "join" && request.method === "POST") {
    const body = await readJson<{ name?: unknown }>(request);
    return Response.json(await stub.join(cleanName(body.name)), { status: 201 });
  }

  const token = bearerToken(request);
  if (parts.length === 3 && request.method === "GET") {
    return Response.json(await stub.getSnapshot(token));
  }
  if (parts.length === 4 && request.method === "POST") {
    if (parts[3] === "start") return Response.json(await stub.start(token));
    if (parts[3] === "reveal") return Response.json(await stub.reveal(token));
    if (parts[3] === "next") return Response.json(await stub.next(token));
    if (parts[3] === "answer") {
      const body = await readJson<{ answerIndex?: unknown }>(request);
      if (typeof body.answerIndex !== "number") throw new PartyError(400, "Missing answer.");
      return Response.json(await stub.answer(token, body.answerIndex));
    }
  }
  throw new PartyError(404, "Not found.");
}

function rpcStatus(message: string): number {
  if (message === "Party not found.") return 404;
  if (message === "Your party session has expired.") return 401;
  if (message === "Only the host can do that.") return 403;
  if (["This game has already started.", "This party is full.", "Answers are not open right now.", "There is no question to reveal.", "The current question is unavailable.", "Reveal the answer first."].includes(message)) return 409;
  if (["Invalid answer.", "Invalid game settings.", "Choose 5, 10, or 20 questions.", "Invalid question list.", "Questions must be unique."].includes(message)) return 400;
  return 500;
}

function newPlayer(name: string): StoredPlayer {
  return { id: crypto.randomUUID(), token: crypto.randomUUID(), name, score: 0, answers: {} };
}

function authenticate(room: StoredRoom, token: string): StoredPlayer {
  const player = room.players.find((candidate) => candidate.token === token);
  if (!player) throw new PartyError(401, "Your party session has expired.");
  return player;
}

function authenticateHost(room: StoredRoom, token: string): StoredPlayer {
  const player = authenticate(room, token);
  if (player.id !== room.hostPlayerId) throw new PartyError(403, "Only the host can do that.");
  return player;
}

function validateSettings(settings: RoomSettings, questions: PartyQuestion[]): void {
  if (typeof settings.category !== "string" || typeof settings.difficulty !== "string") {
    throw new PartyError(400, "Invalid game settings.");
  }
  if (![5, 10, 20].includes(settings.questionCount) || questions.length !== settings.questionCount) {
    throw new PartyError(400, "Choose 5, 10, or 20 questions.");
  }
  if (questions.some((question) => typeof question.id !== "string" || question.id.length < 1 || question.id.length > 100 || !Number.isInteger(question.correctIndex) || question.correctIndex < 0 || question.correctIndex > 5)) {
    throw new PartyError(400, "Invalid question list.");
  }
  if (new Set(questions.map((question) => question.id)).size !== questions.length) {
    throw new PartyError(400, "Questions must be unique.");
  }
}

function cleanName(value: unknown): string {
  if (typeof value !== "string") throw new PartyError(400, "Enter your name.");
  const name = value.trim().replace(/\s+/g, " ");
  if (name.length < 1 || name.length > 24) throw new PartyError(400, "Names must be 1–24 characters.");
  return name;
}

function normalizeCode(value: string | undefined): string {
  const code = (value ?? "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (code.length !== 6) throw new PartyError(400, "Enter the six-character party code.");
  return code;
}

function randomCode(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  return Array.from(bytes, (byte) => CODE_ALPHABET[byte % CODE_ALPHABET.length]).join("");
}

function bearerToken(request: Request): string {
  const header = request.headers.get("Authorization") ?? "";
  if (!header.startsWith("Bearer ") || header.length < 20) throw new PartyError(401, "Missing party session.");
  return header.slice(7);
}

async function readJson<T>(request: Request): Promise<T> {
  const contentLength = Number(request.headers.get("Content-Length") ?? "0");
  if (contentLength > 32_000) throw new PartyError(413, "Request is too large.");
  try {
    return await request.json<T>();
  } catch {
    throw new PartyError(400, "Invalid request.");
  }
}

function withCors(response: Response): Response {
  const headers = new Headers(response.headers);
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Authorization, Content-Type");
  headers.set("Cache-Control", "no-store");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
}
