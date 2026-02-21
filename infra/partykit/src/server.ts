import type * as Party from "partykit/server";

export default class PRRoom implements Party.Server {
  constructor(readonly room: Party.Room) {}

  onConnect(conn: Party.Connection, ctx: Party.ConnectionContext) {
    // Stub: will be implemented in Phase 11
    console.log(`Connection opened: ${conn.id}`);
  }

  onMessage(message: string, sender: Party.Connection) {
    // Stub: will be implemented in Phase 11
    console.log(`Message from ${sender.id}: ${message}`);
  }
}
