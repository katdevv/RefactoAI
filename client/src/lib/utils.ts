import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ResponseItem {
  id: number;
  topic: string;
  name: string;
}

// 🔹 Groups tasks by topic fetched from backend
export const grouper = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    console.log("API:", apiUrl);

    const res = await fetch(`${apiUrl}/tasks`, {
      headers: { Accept: "application/json" },
    });

    // Handle unexpected response (HTML, empty, etc.)
    const text = await res.text();
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
    }
    if (!text.trim().startsWith("{") && !text.trim().startsWith("[")) {
      throw new SyntaxError(
        `Expected JSON but got unexpected content: ${text.slice(0, 100)}`
      );
    }

    const response = JSON.parse(text);
    const rawData: ResponseItem[] = response.tasks || response;

    const grouped = rawData.reduce((acc, task) => {
      let group = acc.find((g) => g.topic === task.topic);
      if (!group) {
        group = { topic: task.topic, tasks: [] };
        acc.push(group);
      }
      group.tasks.push({ name: task.name, id: task.id });
      return acc;
    }, [] as { topic: string; tasks: { name: string; id: number }[] }[]);

    return grouped;
  } catch (err) {
    console.error("❌ Error in grouper:", err);
    throw new Error("Something went wrong while grouping data.");
  }
};
