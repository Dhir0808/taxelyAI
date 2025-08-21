export const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") || "http://localhost:8010";
export const SHEETS_IMPORT_URL = `${BACKEND}/api/sheets/import`;
export const WAIT_URL = `${BACKEND}/api/portia/wait`;
export const SHEETS_LIST_URL = `${BACKEND}/api/sheets/list`;
