export class CLIOutput {
  public static info(msg: string): void {
    console.log(`\x1b[36mℹ [INFO]\x1b[0m ${msg}`);
  }

  public static success(msg: string): void {
    console.log(`\x1b[32m✔ [SUCCESS]\x1b[0m ${msg}`);
  }

  public static warn(msg: string): void {
    console.warn(`\x1b[33m⚠ [WARNING]\x1b[0m ${msg}`);
  }

  public static error(msg: string): void {
    console.error(`\x1b[31m✖ [ERROR]\x1b[0m ${msg}`);
  }

  public static header(title: string): void {
    console.log(`\n\x1b[1m\x1b[35m=== ${title} ===\x1b[0m\n`);
  }
}
