"use client";

import { ReactNode } from "react";
import Modal from "./Modal";
import {
  usePreferencesStore,
  type ClockType,
  type ClockFormat,
} from "@/stores/preferencesStore";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({
  isOpen,
  onClose,
}: SettingsModalProps): ReactNode {
  const clockType = usePreferencesStore((s) => s.clockType);
  const clockFormat = usePreferencesStore((s) => s.clockFormat);
  const setClockType = usePreferencesStore((s) => s.setClockType);
  const setClockFormat = usePreferencesStore((s) => s.setClockFormat);

  const handleClockTypeChange = (type: ClockType) => {
    setClockType(type);
  };

  const handleClockFormatChange = (format: ClockFormat) => {
    setClockFormat(format);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Settings"
      footer={
        <button
          onClick={onClose}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-bold rounded-lg transition-colors"
        >
          Close
        </button>
      }
    >
      <div className="space-y-6">
        {/* Clock Type */}
        <div>
          <label className="block text-slate-400 text-xs font-bold uppercase tracking-wider mb-3">
            Clock Type
          </label>
          <div className="flex gap-3">
            <button
              onClick={() => handleClockTypeChange("analog")}
              className={`flex-1 px-4 py-3 rounded-lg border text-sm font-bold transition-colors ${
                clockType === "analog"
                  ? "bg-purple-500/20 border-purple-500 text-purple-300"
                  : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
              }`}
            >
              Analog
            </button>
            <button
              onClick={() => handleClockTypeChange("digital")}
              className={`flex-1 px-4 py-3 rounded-lg border text-sm font-bold transition-colors ${
                clockType === "digital"
                  ? "bg-purple-500/20 border-purple-500 text-purple-300"
                  : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
              }`}
            >
              Digital
            </button>
          </div>
        </div>

        {/* Time Format - only visible when digital */}
        {clockType === "digital" && (
          <div>
            <label className="block text-slate-400 text-xs font-bold uppercase tracking-wider mb-3">
              Time Format
            </label>
            <div className="flex gap-3">
              <button
                onClick={() => handleClockFormatChange("12h")}
                className={`flex-1 px-4 py-3 rounded-lg border text-sm font-bold transition-colors ${
                  clockFormat === "12h"
                    ? "bg-purple-500/20 border-purple-500 text-purple-300"
                    : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
                }`}
              >
                12-hour
              </button>
              <button
                onClick={() => handleClockFormatChange("24h")}
                className={`flex-1 px-4 py-3 rounded-lg border text-sm font-bold transition-colors ${
                  clockFormat === "24h"
                    ? "bg-purple-500/20 border-purple-500 text-purple-300"
                    : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
                }`}
              >
                24-hour
              </button>
            </div>
          </div>
        )}

        {/* Tip */}
        <div className="pt-4 border-t border-slate-800">
          <p className="text-slate-500 text-xs">
            Tip: Click the clock in the office to quickly cycle between modes.
          </p>
        </div>
      </div>
    </Modal>
  );
}
