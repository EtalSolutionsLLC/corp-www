const now = new Date();

const parts = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false
}).formatToParts(now);

const hour = parts.find((p) => p.type === "hour")?.value;
const minute = parts.find((p) => p.type === "minute")?.value;

const shouldRun = hour === "00" && minute === "05";

console.log(`Eastern time now: ${hour}:${minute}`);
console.log(`should_run=${shouldRun ? "true" : "false"}`);

process.exit(shouldRun ? 0 : 78);
