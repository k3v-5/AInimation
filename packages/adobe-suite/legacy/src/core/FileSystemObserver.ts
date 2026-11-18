import fs from 'fs';

export class FileSystemObserver {
  /**
   * Polls the filesystem until a file exists, its size stops changing (stabilized),
   * and it can be opened with read/write access (no exclusive locks).
   */
  public async waitForFileStabilization(
    filePath: string,
    checkIntervalMs: number = 1000,
    timeoutMs: number = 30000,
    stabilizationCount: number = 3
  ): Promise<boolean> {
    const startTime = Date.now();
    let previousSize = -1;
    let stableTicks = 0;

    return new Promise((resolve) => {
      const interval = setInterval(() => {
        if (Date.now() - startTime > timeoutMs) {
          clearInterval(interval);
          resolve(false);
          return;
        }

        if (fs.existsSync(filePath)) {
          try {
            const stats = fs.statSync(filePath);
            const currentSize = stats.size;

            if (currentSize === previousSize && currentSize > 0) {
              stableTicks++;
            } else {
              stableTicks = 0;
            }
            previousSize = currentSize;

            if (stableTicks >= stabilizationCount) {
              // Verify the file is not locked by trying to open it for reading
              try {
                const fd = fs.openSync(filePath, 'r+');
                fs.closeSync(fd);
                clearInterval(interval);
                resolve(true);
              } catch (lockError: any) {
                if (lockError.code !== 'EBUSY' && lockError.code !== 'EPERM') {
                   // Some other error, assume stable but perhaps read-only
                   clearInterval(interval);
                   resolve(true);
                }
              }
            }
          } catch (e) {
            // File might be temporarily inaccessible
          }
        }
      }, checkIntervalMs);
    });
  }
}
