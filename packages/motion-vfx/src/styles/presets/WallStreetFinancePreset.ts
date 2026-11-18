export interface CandlestickData {
  open: number;
  close: number;
  high: number;
  low: number;
  timestamp: number;
}

/**
 * Motor Especializado del Preset #12: Wall Street Quantum Finance.
 * Genera velas de trading japonesas animadas (alcistas/bajistas), tickers bursátiles con fluctuación de precios y ticks financieros.
 */
export class WallStreetFinancePreset {
  public static readonly PALETTE = {
    bullishGreen: [0.063, 0.725, 0.506] as [number, number, number], // #10B981
    bearishRed: [0.937, 0.267, 0.267] as [number, number, number], // #EF4444
    deepNavy: [0.039, 0.059, 0.102] as [number, number, number], // #0A0F1A
    gridGray: [0.15, 0.18, 0.25] as [number, number, number], // #262E40
    pureWhite: [1.0, 1.0, 1.0] as [number, number, number], // #FFFFFF
  };

  /**
   * Determina si una vela es alcista o bajista.
   */
  public static isBullish(candle: CandlestickData): boolean {
    return candle.close >= candle.open;
  }

  /**
   * Genera el fragmento ExtendScript para una vela de trading japonesa animada con mechas de sombra.
   */
  public static generateCandlestickSnippet(
    compVar: string,
    candle: CandlestickData,
    positionX: number,
    baseY: number,
    scaleY = 2.0,
    startTimeSec = 0
  ): string {
    const pal = this.PALETTE;
    const isBull = this.isBullish(candle);
    const color = isBull ? pal.bullishGreen : pal.bearishRed;
    const bodyHeight = Math.max(4, Math.abs(candle.close - candle.open) * scaleY);
    const bodyY = baseY - (Math.min(candle.open, candle.close) + Math.abs(candle.close - candle.open) / 2) * scaleY;
    const wickTop = baseY - candle.high * scaleY;
    const wickBottom = baseY - candle.low * scaleY;
    const wickHeight = Math.max(2, wickBottom - wickTop);

    return [
      `// === CANDLESTICK (${candle.timestamp}) ===`,
      `var cLayer = ${compVar}.layers.addShape();`,
      `cLayer.name = "Candle_${candle.timestamp}";`,
      `cLayer.inPoint = ${startTimeSec};`,
      `var cGroup = cLayer.property("Contents").addProperty("ADBE Vector Group");`,
      `// 1. Mecha Superior/Inferior`,
      `var wick = cGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");`,
      `wick.property("Size").setValue([2, ${wickHeight}]);`,
      `// 2. Cuerpo de la Vela`,
      `var body = cGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");`,
      `body.property("Size").setValue([18, ${bodyHeight}]);`,
      `var cFill = cGroup.property("Contents").addProperty("ADBE Vector Graphic - Fill");`,
      `cFill.property("Color").setValue([${color[0]}, ${color[1]}, ${color[2]}]);`,
      `cLayer.transform.position.setValue([${positionX}, ${bodyY}]);`,
      `// Animación de crecimiento vertical`,
      `cLayer.transform.scale.setValueAtTime(${startTimeSec}, [100, 0]);`,
      `cLayer.transform.scale.setValueAtTime(${startTimeSec + 0.3}, [100, 100]);`,
    ].join("\n");
  }

  /**
   * Genera el fragmento ExtendScript para un ticker bursátil dinámico (ej. NASDAQ: +4.25%).
   */
  public static generateStockTickerSnippet(
    compVar: string,
    symbol: string,
    price: number,
    changePct: number,
    position: [number, number]
  ): string {
    const pal = this.PALETTE;
    const isUp = changePct >= 0;
    const color = isUp ? pal.bullishGreen : pal.bearishRed;
    const sign = isUp ? "+" : "";
    const tickerText = `${symbol} $${price.toFixed(2)} (${sign}${changePct.toFixed(2)}%)`;

    return [
      `// === STOCK TICKER (${symbol}) ===`,
      `var ticker = ${compVar}.layers.addText("${tickerText}");`,
      `ticker.name = "Ticker_${symbol}";`,
      `ticker.transform.position.setValue([${position[0]}, ${position[1]}]);`,
      `var tDoc = ticker.property("Source Text").value;`,
      `tDoc.fontSize = 48;`,
      `tDoc.font = "Consolas-Bold";`,
      `tDoc.fillColor = [${color[0]}, ${color[1]}, ${color[2]}];`,
      `ticker.property("Source Text").setValue(tDoc);`,
    ].join("\n");
  }
}
