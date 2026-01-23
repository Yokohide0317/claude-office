"use client";

import { Graphics, TextStyle } from "pixi.js";
import { useState, useCallback, useEffect, type ReactNode } from "react";
import type { ClockFormat } from "@/stores/preferencesStore";

/**
 * DigitalClock - Digital clock display for the office wall
 *
 * Displays current time in digital format with configurable 12h/24h display.
 * Matches the visual dimensions of the analog WallClock.
 */
interface DigitalClockProps {
  format: ClockFormat;
}

export function DigitalClock({ format }: DigitalClockProps): ReactNode {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const formatTime = useCallback(
    (date: Date): string => {
      let hours = date.getHours();
      const mins = date.getMinutes();
      const secs = date.getSeconds();

      if (format === "12h") {
        const period = hours >= 12 ? "PM" : "AM";
        hours = hours % 12 || 12;
        return `${hours}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")} ${period}`;
      }

      return `${hours.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    },
    [format],
  );

  const drawClockFace = useCallback((g: Graphics) => {
    g.clear();
    // Outer black ring (same as analog)
    g.circle(0, 0, 44);
    g.fill(0x000000);
    // Face (same as analog)
    g.circle(0, 0, 40);
    g.fill(0xffffff);
    g.stroke({ width: 4, color: 0x2d3748 });
  }, []);

  const timeString = formatTime(time);
  const fontSize = format === "12h" ? 10 : 14;

  return (
    <>
      <pixiGraphics draw={drawClockFace} />
      <pixiText
        text={timeString}
        anchor={0.5}
        style={
          new TextStyle({
            fontFamily: "monospace",
            fontSize,
            fontWeight: "bold",
            fill: 0x2d3748,
          })
        }
      />
    </>
  );
}
