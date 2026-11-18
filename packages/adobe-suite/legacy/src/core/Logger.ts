import pino from 'pino';
import fsNode from 'fs';
import path from 'path';

// Ensure logs directory exists
const logDir = path.join(process.cwd(), 'logs');
if (!fsNode.existsSync(logDir)) {
  fsNode.mkdirSync(logDir, { recursive: true });
}

// Generate log file name based on date
const dateStr = new Date().toISOString().split('T')[0];
const logFile = path.join(logDir, `engine-${dateStr}.log`);

// Create a Pino logger instance configured for production PM2 monitoring
export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  timestamp: pino.stdTimeFunctions.isoTime,
}, pino.destination(logFile));

export const cliLogger = {
  info: (msg: string, obj?: object) => {
    logger.info(obj || {}, msg);
  },
  error: (msg: string, obj?: object) => {
    logger.error(obj || {}, msg);
  },
  warn: (msg: string, obj?: object) => {
    logger.warn(obj || {}, msg);
  }
};