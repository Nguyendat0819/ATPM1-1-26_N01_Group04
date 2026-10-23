const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../routes/leaves.js"), "utf8");

function fixture(options = {}) {
  const calls = [];
  const logs = [];
  const leave = {
    id: 11,
    user_id: 20,
    status: "PENDING",
    target_role: "STAFF",
    department_id: 7,
    full_name: "Nhân viên",
    reason: "Nghỉ phép",
    start_date: "2026-10-19",
    end_date: "2026-10-20",
    total_days: 2,
    ...options.leave,
  };
  const pool = {
    async query(sql, params) {
      calls.push({ sql, params });
      if (sql.includes("FROM leave_requests lr JOIN users u ON lr.user_id = u.id WHERE lr.id")) {
        return { rows: options.missing ? [] : [leave] };
      }
      if (sql.includes("SELECT department_id as id")) {
        return { rows: [{ id: options.managerDepartment ?? 7 }] };
      }
      if (sql.includes("UPDATE leave_requests")) {
        return { rows: options.updateLostRace ? [] : [{ id: leave.id }] };
      }
      if (sql.includes("SELECT email FROM users")) {
        return { rows: [{ email: "staff@example.test" }] };
      }
      return { rows: [] };
    },
  };
  const handlers = new Map();
  const router = {
    get() {},
    post() {},
    put(route, handler) { handlers.set(route, handler); },
  };
  const context = {
    require(name) {
      if (name === "express") return { Router: () => router };
      if (name === "../db") return pool;
      if (name === "jsonwebtoken") {
        return { verify(token) {
          if (token === "invalid") throw new Error("invalid token");
          return options.user ?? { id: 10, role: "MANAGER" };
        } };
      }
      if (name === "../models/LeaveLog") {
        return { async create(log) {
          if (options.logFailure) throw new Error("Mongo unavailable");
          logs.push(log);
        } };
      }
      throw new Error(`Unexpected import: ${name}`);
    },
    module: { exports: {} },
    process: { env: { JWT_SECRET: "test-secret" } },
    console: { error() {} },
    Date,
    setTimeout,
  };
  vm.runInNewContext(source, context, { filename: "leaves.js" });

  async function invoke(request = {}) {
    const req = {
      params: { id: request.id ?? "11" },
      body: { status: "APPROVED", ...request.body },
      headers: request.headers ?? { authorization: "Bearer valid" },
      app: { get() {
        return options.socketFailure ? { emit() { throw new Error("Socket unavailable"); } } : null;
      } },
    };
    const res = {
      statusCode: 200,
      status(code) { this.statusCode = code; return this; },
      json(body) { this.body = body; return this; },
    };
    await handlers.get("/:id/status")(req, res);
    return res;
  }
  return { invoke, calls, logs };
}

const rejectionCases = [
  { id: "LV-01", name: "không có JWT", request: { headers: {} }, expected: 401 },
  { id: "LV-02", name: "JWT sai", request: { headers: { authorization: "Bearer invalid" } }, expected: 401 },
  { id: "LV-03", name: "ID không hợp lệ", request: { id: "abc" }, expected: 400 },
  { id: "LV-04", name: "trạng thái ngoài APPROVED/REJECTED", request: { body: { status: "CANCELLED" } }, expected: 400 },
  { id: "LV-05", name: "STAFF tự gọi API duyệt", options: { user: { id: 21, role: "STAFF" } }, expected: 403 },
  { id: "LV-06", name: "đơn không tồn tại", options: { missing: true }, expected: 404 },
  { id: "LV-07", name: "MANAGER duyệt đơn phòng khác", options: { managerDepartment: 8 }, expected: 403 },
  { id: "LV-08", name: "MANAGER duyệt MANAGER", options: { leave: { target_role: "MANAGER" } }, expected: 403 },
  { id: "LV-09", name: "ADMIN duyệt STAFF", options: { user: { id: 1, role: "ADMIN" } }, expected: 403 },
  { id: "LV-10", name: "tự duyệt đơn", options: { user: { id: 20, role: "MANAGER" } }, expected: 403 },
  { id: "LV-11", name: "duyệt lại đơn đã xử lý", options: { leave: { status: "APPROVED" } }, expected: 409 },
  { id: "LV-12", name: "hai người duyệt đồng thời", options: { updateLostRace: true }, expected: 409 },
];

for (const item of rejectionCases) {
  test(`${item.id} ${item.name}`, async () => {
    const { invoke, calls, logs } = fixture(item.options);
    const res = await invoke(item.request);
    assert.equal(res.statusCode, item.expected);
    assert.equal(calls.some(call => call.sql.includes("UPDATE leave_requests")), item.id === "LV-12");
    assert.equal(logs.length, 0);
  });
}

test("LV-13 MANAGER duyệt STAFF cùng phòng từ PENDING", async () => {
  const { invoke, calls, logs } = fixture();
  const res = await invoke();
  assert.equal(res.statusCode, 200);
  const update = calls.find(call => call.sql.includes("UPDATE leave_requests"));
  assert.match(update.sql, /WHERE id = \$4 AND status = 'PENDING' RETURNING id/);
  assert.deepEqual(Array.from(update.params), ["APPROVED", 10, null, "11"]);
  assert.equal(logs.length, 1);
  assert.equal(logs[0].performed_by, "MANAGER");
});

test("LV-14 SUPERADMIN từ chối MANAGER từ PENDING", async () => {
  const { invoke, calls } = fixture({
    user: { id: 1, role: "SUPERADMIN" },
    leave: { target_role: "MANAGER" },
  });
  const res = await invoke({ body: { status: "REJECTED", rejection_reason: "Thiếu nhân sự" } });
  assert.equal(res.statusCode, 200);
  const update = calls.find(call => call.sql.includes("UPDATE leave_requests"));
  assert.deepEqual(Array.from(update.params), ["REJECTED", 1, "Thiếu nhân sự", "11"]);
});

test("LV-15 cập nhật PostgreSQL thành công dù MongoDB và Socket.IO lỗi", async () => {
  const { invoke, calls, logs } = fixture({ logFailure: true, socketFailure: true });
  const res = await invoke();
  assert.equal(res.statusCode, 200);
  assert.equal(calls.filter(call => call.sql.includes("UPDATE leave_requests")).length, 1);
  assert.equal(logs.length, 0);
});
